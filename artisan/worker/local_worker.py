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
import platform
import shutil
import socket
import stat
import psutil

from .command import LocalCommand
from .base_worker import BaseWorker
from .file_attrs import stat_to_file_attrs
from ..compat import PY2, PY33, follows_symlinks
from ..exceptions import OperationNotSupported


class LocalWorker(BaseWorker):
    """ Implementation of the :class:`artisan.worker.BaseWorker` interface
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
        # Python 2.x doesn't support the mode='x' flag.
        path = self._normalize_path(path)
        if PY2 and mode == 'x':
            os.open(path, os.O_CREAT | os.O_EXCL)
            mode = 'w'
        return open(path, mode)

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

    def get_cpu_usage(self):
        times = psutil.cpu_times(percpu=False)
        return times.user, times.system, times.idle

    def get_cpu_count(self, physical=False):
        return psutil.cpu_count(logical=not physical)

    def get_memory_usage(self):
        mem = psutil.virtual_memory()
        return mem.total - mem.available, mem.available, mem.total

    def get_swap_usage(self):
        swap = psutil.swap_memory()
        return swap.used, swap.free, swap.total

    def get_disk_usage(self, path=None):
        disk = psutil.disk_usage(path if path is not None else '/')
        return disk.used, disk.free, disk.total

    def get_disk_partitions(self, physical=False):
        part = psutil.disk_partitions(all=not physical)
        return [(p.device, p.mountpoint, p.fstype, p.opts.split(',')) for p in part]

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
