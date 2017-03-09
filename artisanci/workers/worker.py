#           Copyright (c) 2017 Seth Michael Larson
#
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

""" Worker implementation for cross-platform . """

import os
import shutil
import stat
import socket
import tempfile
import platform
import requests
from .command import Command
from .expandvars import expandvars
from ..compat import PY2, PY33, follows_symlinks

__all__ = [
    'Worker'
]


class Worker(object):
    def __init__(self):
        self.environment = os.environ.copy()
        self.build = None

        self._closed = False
        self._cwd = os.getcwd()

    def execute(self, command, environment=None, timeout=None, merge_stderr=False):
        """
        Executes a command on the worker and returns an instance
        of :class:`artisan.Command` in order to track the command
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
        :param bool merge_stderr:
            If True will merge the stderr stream into stdout.
            This is good for commands that output everything
            in stderr to prevent the screen from appearing red.
        :rtype: artisan.Command
        :returns: :class:`artisan.Command` instance.
        """
        if not isinstance(command, (list, str)):
            raise TypeError('Command must be of type list or string.')
        if self.build is not None:
            self.build.notify_watchers('command', command)
        if environment is None:
            environment = self.environment
        command = Command(self, command, environment, merge_stderr=merge_stderr)
        command._wait(timeout=timeout,
                      error_on_timeout=True,
                      error_on_exit=True)
        return command

    @property
    def cwd(self):
        """ The current working directory for the worker. """
        return self._cwd

    def mkdir(self, path):
        """
        Creates a directory if it does not exist.

        :param str path: Path to create directories.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'mkdir %s' % path)
        try:
            os.makedirs(self._normalize_path(path))
        except OSError:
            pass

    def chdir(self, path):
        """
        Changes the current working directory for the worker.

        :param str path: Path to change workers cwd to.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'cd %s' % path)
        cwd = self._normalize_path(path)
        if not os.path.isdir(cwd):
            raise ValueError('`%s` is not a valid directory.' % cwd)
        self._cwd = cwd

    def listdir(self, path='.'):
        """
        Lists all file names in a directory on the worker.

        :param str path: Path to the directory to list.
        :return: List of filenames as strings.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'ls %s' % path)
        return os.listdir(self._normalize_path(path))

    def copy(self, source_path, destination_path):
        """
        Copies a file or directory recursively to a destination directory.

        :param str source_path: File or directory to copy.
        :param str destination_path: Directory to copy the file or directory to.
        """
        if os.path.isdir(source_path):
            self.build.notify_watchers('command', 'cp -r %s %s' % (source_path, destination_path))
            shutil.copytree(source_path, os.path.join(destination_path, os.path.basename(source_path)))
        else:
            self.build.notify_watchers('command', 'cp %s %s' % (source_path, destination_path))
            shutil.copy(source_path, destination_path)

    def chmod(self, path, mode, follow_symlinks=True):
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

        if self.build is not None:
            self.build.notify_watchers('command', 'chmod %s %s' % (str(oct(mode)).lstrip('0o'),
                                                                   path))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chmod'):
            os.chmod(path, mode, follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chmod(path, mode)

    def chown(self, path, user_id, follow_symlinks=True):
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
        if self.build is not None:
            self.build.notify_watchers('command', 'chown %s %d %d' % (path, user_id, st.st_gid))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, user_id, st.st_gid,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, user_id, st.st_gid)

    def chgrp(self, path, group_id, follow_symlinks=True):
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
        if self.build is not None:
            self.build.notify_watchers('command', 'chown %s %d %d' % (path, st.st_uid, group_id))
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, st.st_uid, group_id,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, st.st_uid, group_id)

    def stat(self, path, follow_symlinks=True):
        """
        Gets the attributes about a file on the worker's machine.

        :param str path: Path of the file/directory to get attributes from.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        :returns: :class:`artisan.worker.FileAttributes` object.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'stat %s' % path)
        st = _stat_follow(self._normalize_path(path), follow_symlinks)
        return st

    def isdir(self, path):
        """
        Checks to see if a path is a directory.

        :param str path: Path to the directory.
        :returns: True if the path is a directory, False otherwise.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'test -d %s' % path)
        return os.path.isdir(self._normalize_path(path))

    def isfile(self, path):
        """
        Checks to see if a path is a file.

        :param str path: Path to the file.
        :returns: True if the path is a file, False otherwise.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'test -f %s' % path)
        return os.path.isfile(self._normalize_path(path))

    def islink(self, path):
        """
        Checks to see if a path is a symlink.

        :param str path: Path to the symlink.
        :returns: True if the path is a symlink, False otherwise.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'test -L %s' % path)
        path = expandvars(self, os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return stat.S_ISLNK(os.lstat(path).st_mode)

    def open(self, path, mode='r'):
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

    def remove(self, path):
        """
        Removes a file that exists at a path.

        :param str path: Path to the file to remove.
        """
        norm_path = self._normalize_path(path)
        if os.path.isdir(path):
            if self.build is not None:
                self.build.notify_watchers('command', 'rm -rf %s' % path)
            shutil.rmtree(norm_path, ignore_errors=True)
        else:
            if self.build is not None:
                self.build.notify_watchers('command', 'rm %s' % path)
            os.remove(norm_path)

    def symlink(self, source_path, link_path):
        """
        Creates a symbolic link to a source file or directory.

        :param str source_path: Path of the file or directory to link to.
        :param str link_path: Path to the symbolic link.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'ln -s %s %s' % (source_path, link_path))
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

    def download(self, url, path):
        """
        Attempts to download a file from a website given a URL.
        Returns the return code of the HTTP request.

        :param str url: URL to download the file from.
        :param str path: Path to save the file to.
        :returns: HTTP code of the request as an :class:`int`.
        """
        if self.build is not None:
            self.build.notify_watchers('command', 'curl %s --output %s' % (url, path))
        r = requests.get(url, stream=True)
        with self.open(path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return r.status_code

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
