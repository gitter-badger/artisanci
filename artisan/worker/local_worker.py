import os
import shutil
import socket
import stat
import platform

from .base_worker import BaseWorker
from .file_attrs import stat_to_file_attrs
from ..command import LocalCommand
from ..compat import PY33, follows_symlinks
from ..exceptions import OperationNotSupported


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

    def change_file_mode(self, path, mode, follow_symlinks=True):
        if platform.system() == 'Windows':
            st = _stat_follow(path, follow_symlinks)
            # The only two bits that aren't ignored on Windows are
            # stat.S_IREAD and stat.S_IWRITE. Error if anything
            # is changed besides those two.
            if (mode ^ st.st_mode) & ~(stat.S_IREAD | stat.S_IWRITE):
                raise OperationNotSupported('change_file_mode()', 'Windows LocalWorker')
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chmod'):
            os.chmod(path, mode, follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chmod(path, mode)

    def change_file_owner(self, path, user_id, follow_symlinks=True):
        _check_chown_support()
        st = _stat_follow(path, follow_symlinks)
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, user_id, st.st_gid,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, user_id, st.st_gid)

    def change_file_group(self, path, group_id, follow_symlinks=True):
        _check_chown_support()
        st = _stat_follow(path, follow_symlinks)
        path = self._normalize_path(path)
        if PY33 and follows_symlinks('os.chown'):
            os.chown(path, st.st_uid, group_id,
                     follow_symlinks=follow_symlinks)
        else:
            if follow_symlinks:
                path = os.path.realpath(path)
            os.chown(path, st.st_uid, group_id)

    def stat_file(self, path, follow_symlinks=True):
        st = _stat_follow(self._normalize_path(path), follow_symlinks)
        return stat_to_file_attrs(st)

    def is_directory(self, path):
        return os.path.isdir(self._normalize_path(path))

    def is_file(self, path):
        return os.path.isfile(self._normalize_path(path))

    def is_symlink(self, path):
        path = self._expandvars(os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return stat.S_ISLNK(os.lstat(path).st_mode)

    def open_file(self, path, mode='r'):
        return open(self._normalize_path(path), mode)

    def remove_file(self, path):
        os.remove(self._normalize_path(path))

    def remove_directory(self, path):
        shutil.rmtree(self._normalize_path(path), ignore_errors=True)

    def create_symlink(self, source_path, link_path):
        os.symlink(self._normalize_path(source_path),
                   self._normalize_path(link_path))

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
        path = self._expandvars(os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self._cwd, path)
        return os.path.normpath(path)


def _check_chown_support():
    if not hasattr(os, 'chown') or platform.system() == 'Windows':
        raise OperationNotSupported('change_file_owner()', 'Windows LocalWorker')


def _stat_follow(path, follow_symlinks=True):
    if follow_symlinks:
        return os.stat(path)
    else:
        return os.lstat(path)
