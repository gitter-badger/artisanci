from ..exceptions import OperationNotSupported
__all__ = [
    'BaseWorker'
]


class BaseWorker(object):
    def __init__(self, host, environment=None):
        if environment is None:
            environment = self._get_default_environment()

        self.host = host
        self.environment = environment

        self._closed = False

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
        :return: :class:`artisan.BaseCommand` instance.
        """
        raise OperationNotSupported('execute()', 'worker')

    @property
    def cwd(self):
        """
        The current working directory for the worker.
        """
        raise OperationNotSupported('cwd', 'worker')

    def change_directory(self, path):
        """
        Changes the current working directory for the worker.
        :param str path: Path to change workers cwd to.
        """
        raise OperationNotSupported('change_directory()', 'worker')

    def list_directory(self, path="."):
        """
        Lists all file names in a directory on the worker.
        :param str path: Path to the directory to list.
        :return: List of filenames as strings.
        """
        raise OperationNotSupported('list_directory()', 'worker')

    def get_file(self, remote_path, local_path):
        """
        Gets a file from the worker and puts it into a
        local directory.
        :param str remote_path: Path to the file on the worker.
        :param str local_path: Local directory to put the file.
        """
        raise OperationNotSupported('get_file()', 'worker')

    def put_file(self, local_path, remote_path):
        """
        Puts a file from the local machine onto
        the workers file system.
        :param str local_path: Path to the file on the local machine.
        :param str remote_path: Directory on the worker to put the file.
        :return:
        """
        raise OperationNotSupported('put_file()', 'worker')

    def stat_file(self, path, follow_symlinks=True):
        """
        Gets the attributes about a file on the worker's machine.

        :param str path: Path of the file/directory to get attributes from.
        :param bool follow_symlinks: If True, will follow symlinks. Set to False to stat symlinks.
        :return: :class:`artisan.FileAttributes` object.
        """
        raise OperationNotSupported('stat_file()', 'worker')

    def is_directory(self, path):
        """
        Checks to see if a path is a directory.
        :param str path: Path to the directory.
        :return: True if the path is a directory, False otherwise.
        """
        raise OperationNotSupported('is_directory()', 'worker')

    def is_file(self, path):
        """
        Checks to see if a path is a file.
        :param str path: Path to the file.
        :return: True if the path is a file, False otherwise.
        """
        raise OperationNotSupported('is_file()', 'worker')

    def open_file(self, path, mode="r"):
        """
        Opens a file on the worker machine for reading, writing, appending
        in the same way that :meth:`open` works on a local machine.
        Can be used as a context manager just like normal files:

         .. code-block:: python

            with worker.open_file('test.txt', 'w') as f:
                f.write("Hello, world!")

        :param str path: Path to the file to open.
        :param str mode:
            Mode to open the file. This is the same for :meth:`open`.
            See `Python docs <https://docs.python.org/3/library/functions.html#open>`_
            for more information about this parameter. Default is read-only.
        :return: File-like object.
        """
        raise OperationNotSupported('open_file()', 'worker')

    def remove_file(self, path):
        raise OperationNotSupported('remove_file()', 'worker')

    @property
    def closed(self):
        return self._closed

    def close(self):
        """
        Closes the worker and cleans up all resources that the
        worker may be using internally to operate.
        """
        if self._closed:
            raise ValueError("Worker is already closed.")
        self._closed = True

    def _get_default_environment(self):
        raise NotImplementedError()
