import os
import shutil
import socket
import platform

from .base_worker import BaseWorker
from .file_attrs import stat_to_file_attrs
from ..command import LocalCommand


class LocalWorker(BaseWorker):
    """ Implementation of the :class:`artisan.BaseWorker` interface
    that operates on the local machine that Artisan is currently
    running on. """
    def __init__(self):
        self._cwd = os.getcwd()
        super(LocalWorker, self).__init__('localhost')

    def execute(self, command, environment=None):
        if environment is None:
            environment = self.environment
        command = LocalCommand(self, command, environment)
        return command

    def change_directory(self, path):
        self._cwd = self._normalize_path(path)

    @property
    def cwd(self):
        return self._cwd

    def list_directory(self, path='.'):
        return os.listdir(self._normalize_path(path))

    def get_file(self, remote_path, local_path):
        shutil.move(self._normalize_path(remote_path),
                    self._normalize_path(local_path))

    def put_file(self, local_path, remote_path):
        shutil.move(self._normalize_path(local_path),
                    self._normalize_path(remote_path))

    def stat_file(self, path, follow_symlinks=True):
        path = self._normalize_path(path)
        if follow_symlinks:
            stat = os.stat(path)
        else:
            stat = os.lstat(path)
        return stat_to_file_attrs(stat)

    def is_directory(self, path):
        return os.path.isdir(self._normalize_path(path))

    def is_file(self, path):
        return os.path.isfile(self._normalize_path(path))

    def open_file(self, path, mode='r'):
        return open(self._normalize_path(path), mode)

    def remove_file(self, path):
        os.remove(self._normalize_path(path))

    def remove_directory(self, path):
        shutil.rmtree(self._normalize_path(path), ignore_errors=True)

    @property
    def platform(self):
        return platform.system()

    @property
    def hostname(self):
        return socket.gethostname()

    @property
    def home(self):
        return os.path.expanduser('~')

    def _get_default_environment(self):
        return os.environ.copy()

    def _normalize_path(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return os.path.normpath(self._expandvars(os.path.expanduser(path)))
