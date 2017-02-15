""" Definition of the BaseWorker interface. """

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

from .expandvars import expandvars
from ..exceptions import OperationNotSupported

__all__ = [
    'BaseWorker'
]


class BaseWorker(object):
    def __init__(self, report):
        self.environment = self._get_default_environment()

        self._closed = False
        self._report = report

    def execute(self, command, environment=None):
        """
        Executes a command on the worker and returns an instance
        of :class:`artisan.BaseCommand` in order to track the command
        call.

        :param command:
            Either a list of strings or a string. If using a string
            the command will be executed as a shell session.
        :param environment:
            Optional dictionary of key-value pairs for environment
            variables to override the default worker environment.
        :rtype: artisan.BaseCommand
        :returns: :class:`artisan.BaseCommand` instance.
        """
        raise OperationNotSupported('execute()', self._get_implementation_name())

    @property
    def cwd(self):
        """ The current working directory for the worker. """
        raise OperationNotSupported('cwd', self._get_implementation_name())

    @property
    def pathlib(self):
        """ The pathlib to use for path manipulations of the worker. """
        raise NotImplementedError()

    @property
    def report(self):
        return self._report

    def create_directory(self, path):
        """
        Creates a directory if it does not exist.

        :param str path: Path to create directories.
        """
        raise OperationNotSupported('create_directory()', self._get_implementation_name())

    def change_directory(self, path):
        """
        Changes the current working directory for the worker.

        :param str path: Path to change workers cwd to.
        """
        raise OperationNotSupported('change_directory()', self._get_implementation_name())

    def list_directory(self, path='.'):
        """
        Lists all file names in a directory on the worker.

        :param str path: Path to the directory to list.
        :return: List of filenames as strings.
        """
        raise OperationNotSupported('list_directory()', self._get_implementation_name())

    def get_file(self, remote_path, local_path):
        """
        Gets a file from the worker and puts it into a
        local directory.

        :param str remote_path: Path to the file on the worker.
        :param str local_path: Local directory to put the file.
        """
        raise OperationNotSupported('get_file()', self._get_implementation_name())

    def put_file(self, local_path, remote_path):
        """
        Puts a file from the local machine onto
        the workers file system.

        :param str local_path: Path to the file on the local machine.
        :param str remote_path: Directory on the worker to put the file.
        """
        raise OperationNotSupported('put_file()', self._get_implementation_name())

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
        raise OperationNotSupported('change_file_mode()', self._get_implementation_name())

    def change_file_owner(self, path, user_id, follow_symlinks=True):
        """
        Changes a file's owner to a different UID.

         .. warning::
            This function is not supported on Windows.

        :param str path: Path to the file or directory.
        :param int user_id: UID of the file's new owner.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        """
        raise OperationNotSupported('change_file_owner()', self._get_implementation_name())

    def change_file_group(self, path, group_id, follow_symlinks=True):
        """
        Changes a file's group to a different GID.

         .. warning::
            This function is not supported on Windows.

        :param str path: Path to the file or directory.
        :param int group_id: GID of the files new group.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        """
        raise OperationNotSupported('change_file_group()', self._get_implementation_name())

    def stat_file(self, path, follow_symlinks=True):
        """
        Gets the attributes about a file on the worker's machine.

        :param str path: Path of the file/directory to get attributes from.
        :param bool follow_symlinks: If True will follow symlinks in the path.
        :returns: :class:`artisan.worker.FileAttributes` object.
        """
        raise OperationNotSupported('stat_file()', self._get_implementation_name())

    def is_directory(self, path):
        """
        Checks to see if a path is a directory.

        :param str path: Path to the directory.
        :returns: True if the path is a directory, False otherwise.
        """
        raise OperationNotSupported('is_directory()', self._get_implementation_name())

    def is_file(self, path):
        """
        Checks to see if a path is a file.

        :param str path: Path to the file.
        :returns: True if the path is a file, False otherwise.
        """
        raise OperationNotSupported('is_file()', self._get_implementation_name())

    def is_symlink(self, path):
        """
        Checks to see if a path is a symlink.

        :param str path: Path to the symlink.
        :returns: True if the path is a symlink, False otherwise.
        """
        raise OperationNotSupported('is_symlink()', self._get_implementation_name())

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
        raise OperationNotSupported('open_file()', self._get_implementation_name())

    def remove_file(self, path):
        """
        Removes a file that exists at a path.

        :param str path: Path to the file to remove.
        """
        raise OperationNotSupported('remove_file()', self._get_implementation_name())

    def remove_directory(self, path):
        """
        Removes a directory that exists at a path.

        :param str path: Path to the directory to remove.
        """
        raise OperationNotSupported('remove_directory()', self._get_implementation_name())

    def create_symlink(self, source_path, link_path):
        """
        Creates a symbolic link to a source file or directory.

        :param str source_path: Path of the file or directory to link to.
        :param str link_path: Path to the symbolic link.
        :raises: :class:`artisan.OperationNotSupported` on Windows.
        """
        raise OperationNotSupported('create_symlink', self._get_implementation_name())

    @property
    def platform(self):
        """ Gets the name of the platform that the worker is on.
        Can be either 'Linux', 'Mac OS', 'Windows', or another OS name. """
        raise OperationNotSupported('platform', self._get_implementation_name())

    @property
    def hostname(self):
        """ Gets the hostname for the machine the worker is on. """
        raise OperationNotSupported('hostname', self._get_implementation_name())

    @property
    def home(self):
        """ Gets the home directory for the worker. """
        raise OperationNotSupported('home', self._get_implementation_name())

    @property
    def tmp(self):
        """ Gets the temporary directory for the worker. """
        raise OperationNotSupported('tmp', self._get_implementation_name())

    def get_cpu_usage(self):
        """
        Gets the amount of CPU seconds that have been spent in each mode.
        The three modes are ``user``, ``system``, and ``idle``. The results
        are returned as a tuple of (user, system, idle).

        :returns: :class:`tuple` containing (user, system, and idle) as :class:`float`.
        """
        raise OperationNotSupported('get_cpu_usage()', self._get_implementation_name())

    def get_cpu_count(self, physical=False):
        """
        Gets the number of CPUs that the worker's machine has.

        :param bool physical:
            If True will only return physical CPU cores only.
            Hyper-threaded cores will be excluded.
        :returns: Number of cores as an :class:`int`.
        """
        raise OperationNotSupported('get_cpu_count()', self._get_implementation_name())

    def get_memory_usage(self):
        """
        Gets the values for virtual memory usage by the worker.
        Values are expressed in bytes as :class:`int`.

        :returns: :class:`tuple` containing the (used, available, and total) virtual memory.
        """
        raise OperationNotSupported('get_memory_usage()', self._get_implementation_name())

    def get_swap_usage(self):
        """
        Gets the values for swap memory usage by the worker.
        Values are expressed in bytes as :class:`int`.

        :returns: :class:`tuple` containing the (used, available, and total) swap memory.
        """
        raise OperationNotSupported('get_swap_usage()', self._get_implementation_name())

    def get_disk_usage(self, path=None):
        """
        Gets the usage information for the disk.
        All values are expressed in bytes as :class:`int`.

        :param str path: Optional value for the path to use to find disk space from.
        :returns: :class:`tuple` containing the (used, available, and total) disk space.
        """
        raise OperationNotSupported('get_disk_usage()', self._get_implementation_name())

    def get_disk_partitions(self, physical=False):
        """
        Gets a list of all mounted disk partitions including device, mount,
        filesystem type, and options.

        :param bool physical:
            If True will try to exclude all non-physical mount
            points from the results.
        :returns: List of :class:`tuple` that contain (device, mount, fstype, and options)
        """
        raise OperationNotSupported('get_disk_partitions()', self._get_implementation_name())

    def download_file(self, url, path):
        """
        Attempts to download a file from a website given a URL.
        Returns the return code of the HTTP request.

        :param str url: URL to download the file from.
        :param str path: Path to save the file to.
        :returns: HTTP code of the request as an :class:`int`.
        """
        raise OperationNotSupported('download_file()', self._get_implementation_name())

    @property
    def closed(self):
        """ Boolean property that is ``True`` if the worker is closed. """
        return self._closed

    def close(self):
        """ Closes the worker and cleans up all resources that the
        worker may be using internally to operate. """
        if self._closed:
            raise ValueError('Worker is already closed.')
        self._closed = True

    def _get_default_environment(self):
        raise NotImplementedError()

    def _expandvars(self, path):
        return expandvars(self, path)

    def _set_environment(self, name, value):
        self.environment[name] = value

    def _del_environment(self, name):
        del self.environment[name]

    def _get_implementation_name(self):
        return type(self).__name__

    def __repr__(self):
        return '<%s host=`%s`>' % (type(self).__name__, self.host)

    def __str__(self):
        return self.__repr__()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if not self._closed:
            try:
                self.close()
            except ValueError:  # Skip coverage.
                pass
