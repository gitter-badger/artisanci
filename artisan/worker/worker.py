""" Definition of the Worker interface. """

#           Copyright (c) 2017 Seth Michael Larson
# _________________________________________________________________
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os
import shutil
import stat
import socket
import tempfile
import platform
import requests
from .command import Command
from .expandvars import expandvars
from .file_attrs import stat_to_file_attrs
from ..compat import PY2, PY33, follows_symlinks

__all__ = [
    'Worker'
]


class Worker(object):
    def __init__(self):
        self.environment = os.environ.copy()

        self._closed = False
        self._cwd = os.getcwd()
        self._listeners = []

    def add_listener(self, listener):
        if listener in self._listeners:
            raise ValueError('This listener is already listening.')
        self._listeners.append(listener)

    def remove_listener(self, listener):
        if listener not in self._listeners:
            raise ValueError('This listener is not listening.')
        self._listeners.remove(listener)

    def _notify_listeners(self, event_type, event_data):
        event_func = 'on_' + event_type
        for listener in self._listeners:
            if hasattr(listener, event_func):
                getattr(listener, event_func)(event_data)

    def execute(self, command, environment=None, timeout=None):
        """
        Executes a command on the worker and returns an instance
        of :class:`artisan.BaseCommand` in order to track the command
        call.

        :param str command:
            Either a list of strings or a string. If using a string
            the command will be executed as a shell session.
        :param dict environment:
            Optional dictionary of key-value pairs for environment
            variables to override the default worker environment.
        :param float timeout:
            Number of seconds to wait before the command errors
            with a timeout exception.
        :rtype: artisan.Command
        :returns: :class:`artisan.Command` instance.
        """
        if not isinstance(command, (list, str)):
            raise TypeError('Command must be of type list or string.')
        if environment is None:
            environment = self.environment
        if isinstance(command, list):
            self._notify_listeners('next_command', ' '.join(command))
        else:
            self._notify_listeners('next_command', command)
        command = Command(self, command, environment)
        command.wait(timeout=timeout,
                     error_on_timeout=True,
                     error_on_exit=True)
        return command

    @property
    def cwd(self):
        """ The current working directory for the worker. """
        return self._cwd

    @property
    def path(self):
        """ The path to use for path manipulations of the worker. """
        raise NotImplementedError()

    def create_directory(self, path):
        """
        Creates a directory if it does not exist.

        :param str path: Path to create directories.
        """
        self._notify_listeners('next_command', 'mkdir %s' % path)
        try:
            os.makedirs(self._normalize_path(path))
        except OSError:
            pass

    def change_directory(self, path):
        """
        Changes the current working directory for the worker.

        :param str path: Path to change workers cwd to.
        """
        self._notify_listeners('next_command', 'cd %s' % path)
        self._cwd = self._normalize_path(path)

    def list_directory(self, path='.'):
        """
        Lists all file names in a directory on the worker.

        :param str path: Path to the directory to list.
        :return: List of filenames as strings.
        """
        self._notify_listeners('next_command', 'ls %s' % path)
        return os.listdir(self._normalize_path(path))

    def change_file_mode(self, path, mode, follow_symlinks=True):
        """
        Change a file's mode.

         .. warning::
            This function is not supported on Windows except
            for :py:attr:`stat.S_IREAD` and :py:attr:`stat.S_IWRITE`.

        :param str path: Path to the file or directory.
        :param int mode:
            Combination of stat.S_* entities bitwise ORed together. See
            `documentation on os.chmod <https://docs.python.org/3.6/library/os.html#os.chmod>`_
            for more information on these flags.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        """
        if platform.system() == 'Windows':
            st = _stat_follow(path, follow_symlinks)
            # The only two bits that aren't ignored on Windows are
            # stat.S_IREAD and stat.S_IWRITE. Error if anything
            # is changed besides those two.
            if (mode ^ st.st_mode) & ~(stat.S_IREAD | stat.S_IWRITE):
                raise NotImplementedError('stat.S_IREAD and stat.S_IWRITE are'
                                          'the only operations supported by Windows.')

        self._notify_listeners('next_command', 'chmod %s %s' % (str(oct(mode)).lstrip('0o'),
                                                                path))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chmod'):
            os.chmod(path, mode, follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chmod(path, mode)

    def change_file_owner(self, path, user_id, follow_symlinks=True):
        """
        Changes a file's owner to a different UID.

         .. warning::
            This function is not supported on Windows.

        :param str path: Path to the file or directory.
        :param int user_id: UID of the file's new owner.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        """
        _check_chown_support()
        st = _stat_follow(path, follow_symlinks)
        self._notify_listeners('next_command', 'chown %s %d %d' % (path, user_id, st.st_gid))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, user_id, st.st_gid,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, user_id, st.st_gid)

    def change_file_group(self, path, group_id, follow_symlinks=True):
        """
        Changes a file's group to a different GID.

         .. warning::
            This function is not supported on Windows.

        :param str path: Path to the file or directory.
        :param int group_id: GID of the files new group.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        """
        _check_chown_support()
        st = _stat_follow(path, follow_symlinks)
        self._notify_listeners('next_command', 'chown %s %d %d' % (path, st.st_uid, group_id))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, st.st_uid, group_id,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, st.st_uid, group_id)

    def stat_file(self, path, follow_symlinks=True):
        """
        Gets the attributes about a file on the worker's machine.

        :param str path: Path of the file/directory to get attributes from.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        :returns: :class:`artisan.worker.FileAttributes` object.
        """
        st = _stat_follow(self._normalize_path(path), follow_symlinks)
        self._notify_listeners('next_command', 'stat %s' % path)
        return stat_to_file_attrs(st)

    def is_directory(self, path):
        """
        Checks to see if a path is a directory.

        :param str path: Path to the directory.
        :returns: True if the path is a directory, False otherwise.
        """
        self._notify_listeners('next_command', 'test -d %s' % path)
        return os.path.isdir(self._normalize_path(path))

    def is_file(self, path):
        """
        Checks to see if a path is a file.

        :param str path: Path to the file.
        :returns: True if the path is a file, False otherwise.
        """
        self._notify_listeners('next_command', 'test -f %s' % path)
        return os.path.isfile(self._normalize_path(path))

    def is_symlink(self, path):
        """
        Checks to see if a path is a symlink.

        :param str path: Path to the symlink.
        :returns: True if the path is a symlink, False otherwise.
        """
        self._notify_listeners('next_command', 'test -L %s' % path)
        path = self._expandvars(os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return stat.S_ISLNK(os.lstat(path).st_mode)

    def open_file(self, path, mode='r'):
        """
        Opens a file on the worker machine for reading, writing, appending
        in the same way that :meth:`open` works on a local machine.
        Can be used as a context manager just like normal files:

         .. code-block:: python

            with worker.open_file('test.txt', 'w') as f:
                f.write('Hello, world!')

        :param str path: Path to the file to open.
        :param str mode:
            Mode to open the file. This is the same for :meth:`open`.
            See `Python docs <https://docs.python.org/3/library/functions.html#open>`_
            for more information about this parameter. Default is read-only.
        :returns: File-like object.
        """
        # Python 2.x doesn't support the mode='x' flag.
        path = self._normalize_path(path)
        if PY2 and mode == 'x':
            os.open(path, os.O_CREAT | os.O_EXCL)
            mode = 'w'
        return open(path, mode)

    def remove_file(self, path):
        """
        Removes a file that exists at a path.

        :param str path: Path to the file to remove.
        """
        self._notify_listeners('next_command', 'rm %s' % path)
        os.remove(self._normalize_path(path))

    def remove_directory(self, path):
        """
        Removes a directory that exists at a path.

        :param str path: Path to the directory to remove.
        """
        self._notify_listeners('next_command', 'rm -rf %s' % path)
        path = self._normalize_path(path)
        shutil.rmtree(path, ignore_errors=True)

    def create_symlink(self, source_path, link_path):
        """
        Creates a symbolic link to a source file or directory.

        :param str source_path: Path of the file or directory to link to.
        :param str link_path: Path to the symbolic link.
        :raises: :class:`artisan.OperationNotSupported` on Windows.
        """
        self._notify_listeners('next_command', 'symlink %s %s' % (source_path, link_path))
        os.symlink(self._normalize_path(source_path),
                   self._normalize_path(link_path))

    @property
    def platform(self):
        """ Gets the name of the platform that the worker is on.
        Can be either 'Linux', 'Mac OS', 'Windows', or another OS name. """
        return platform.system()

    @property
    def hostname(self):
        """ Gets the hostname for the machine the worker is on. """
        return socket.gethostname()

    @property
    def home(self):
        """ Gets the home directory for the worker. """
        return os.path.expanduser('~')

    @property
    def tmp(self):
        """ Gets the temporary directory for the worker. """
        return tempfile.gettempdir()

    def download_file(self, url, path):
        """
        Attempts to download a file from a website given a URL.
        Returns the return code of the HTTP request.

        :param str url: URL to download the file from.
        :param str path: Path to save the file to.
        :returns: HTTP code of the request as an :class:`int`.
        """
        self._notify_listeners('next_command', 'curl %s --output %s' % (url, path))
        r = requests.get(url, stream=True)
        with self.open_file(path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return r.status_code

    def _get_default_environment(self):
        raise NotImplementedError()

    def _normalize_path(self, path):
        path = expandvars(self, os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return os.path.normpath(path)


def _check_chown_support():
    if not hasattr(os, 'chown') or platform.system() == 'Windows':
        raise NotImplementedError('chown is not supported on Windows.')


def _stat_follow(path, follow_symlinks=True):
    if follow_symlinks:
        return os.stat(path)
    else:
        return os.lstat(path)
