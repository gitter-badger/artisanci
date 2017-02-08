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

import functools
import ntpath
import os
import posixpath
import re
import socket
import stat

import paramiko

from .command import SshCommand
from .base_worker import BaseWorker
from .file_attrs import stat_to_file_attrs
from ..exceptions import (OperationNotSupported,
                          WorkerNotAvailable)

__all__ = [
    'SshWorker'
]

_ENV_REGEX = re.compile('^([^=]+)=(.*)$')


# Wrapper function that raises a OperationNotSupported error
# if the worker doesn't have an SFTP client.
def requires_sftp(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if self._sftp is None:
            raise OperationNotSupported(f.__name__, 'worker')
        return f(self, *args, **kwargs)
    return wrapper


class SshWorker(BaseWorker):
    """ Implementation of the :class:`artisan.worker.BaseWorker` interface
    that operates on another machine via SSH and SFTP. """
    def __init__(self, host, username, port=22, environment=None,
                 add_policy=None, **kwargs):

        if add_policy is None:
            add_policy = paramiko.AutoAddPolicy()
        assert isinstance(add_policy, paramiko.MissingHostKeyPolicy)

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(add_policy)
        try:
            self._ssh.connect(host, port, username, **kwargs)
        except (paramiko.SSHException, socket.error):
            raise WorkerNotAvailable()

        # This value is a fall-back if the home directory can't be found.
        self._start_dir = None
        try:
            self._sftp = self._ssh.open_sftp()

            # SFTPClient.getcwd() returns None
            # if chdir() isn't called beforehand.
            self._sftp.chdir('.')
            self._start_dir = self._sftp.getcwd()
        except paramiko.SSHException:
            self._sftp = None  # type: paramiko.SFTPClient

        # Values that are cached after found out.
        self._hostname = None
        self._platform = None
        self._home = None
        self._pathlib = posixpath

        super(SshWorker, self).__init__(host, environment)

        # Some SSH servers allow environment variables to be
        # changed by a client if AcceptEnv is set correctly.
        with self.execute('echo $SILENT_DISCARD_CHECK',
                          environment={'SILENT_DISCARD_CHECK': 'NO'}) as c:
            c.wait(timeout=5.0)
            self.allow_environment_changes = b'NO' in c.stdout.read()

    def execute(self, command, environment=None):
        return SshCommand(self, command, environment)

    @requires_sftp
    def change_directory(self, path):
        self._sftp.chdir(self._normalize_path(path))

    @property
    @requires_sftp
    def cwd(self):
        return self._sftp.getcwd()

    @requires_sftp
    def list_directory(self, path='.'):
        return self._sftp.listdir(self._normalize_path(path))

    @requires_sftp
    def put_file(self, local_path, remote_path):
        self._sftp.put(_normalize_local_path(local_path),
                       self._normalize_path(remote_path))

    @requires_sftp
    def get_file(self, remote_path, local_path):
        self._sftp.get(self._normalize_path(remote_path),
                       _normalize_local_path(local_path))

    @requires_sftp
    def change_file_mode(self, path, mode):
        self._sftp.chmod(self._normalize_path(path), mode)

    @requires_sftp
    def change_file_owner(self, path, user_id):
        st = self.stat_file(path)
        self._sftp.chown(self._normalize_path(path), user_id, st.group_id)

    @requires_sftp
    def change_file_group(self, path, group_id):
        st = self.stat_file(path)
        self._sftp.chown(self._normalize_path(path), st.user_id, group_id)

    @requires_sftp
    def stat_file(self, path, follow_symlinks=True):
        path = self._normalize_path(path)
        if follow_symlinks:
            res = self._sftp.stat(path)
        else:
            res = self._sftp.lstat(path)
        return stat_to_file_attrs(res)

    def is_directory(self, path):
        return stat.S_ISDIR(self.stat_file(path).mode)

    def is_file(self, path):
        return stat.S_ISREG(self.stat_file(path).mode)

    def is_symlink(self, path):
        return stat.S_ISLNK(self.stat_file(path).mode)

    @requires_sftp
    def remove_file(self, path):
        self._sftp.remove(path)

    @requires_sftp
    def remove_directory(self, path):
        self._sftp.rmdir(path)

    @requires_sftp
    def create_symlink(self, source_path, link_path):
        self._sftp.symlink(self._normalize_path(source_path),
                           self._normalize_path(link_path))

    @property
    def home(self):
        if self._home is not None:
            return self._home

        # Try to find it via Python first.
        c = self.execute('python -c "import os, sys; sys.stdout.write(os.expanduser(\'~\'))"')
        if c.wait(timeout=5.0) and c.exit_status == 0:
            self._home = c.stdout.read().decode('utf-8')
            return self._home

        # Linux and Mac OS $HOME directory.
        elif 'HOME' in self.environment:
            self._home = self.environment['HOME']
            return self._home

        # Windows $HOMEPATH directory.
        elif 'HOMEPATH' in self.environment:
            self._home = self.environment['HOMEPATH']
            return self._home

        # Can't find anything else, wherever we landed
        # first is probably the home directory?
        elif self._start_dir is not None:
            self._home = self._start_dir
            return self._home

        # Can't find it and no SFTP client means it's unsupported.
        else:
            raise OperationNotSupported('host', 'worker')

    @property
    def platform(self):
        if self._platform is not None:
            return self._platform
        c = self.execute('python -c "import platform, sys; sys.stdout.write(platform.system())"')
        if c.wait(timeout=5.0) and c.exit_status == 0:
            self._platform = c.stdout.read().decode('utf-8')
            return self._platform
        else:
            raise OperationNotSupported('platform', 'worker')

    @property
    def hostname(self):
        if self._hostname is not None:
            return self._hostname
        c = self.execute('python -c "import socket, sys; sys.stdout.write(socket.gethostname())"')
        if c.wait(timeout=5.0) and c.exit_status == 0:
            self._hostname = c.stdout.read().decode('utf-8')
            return self._hostname
        else:
            raise OperationNotSupported('hostname', 'worker')

    def close(self):
        super(SshWorker, self).close()
        if self._ssh is not None:
            try:
                self._ssh.close()
            except Exception:  # Skip coverage.
                pass
            self._ssh = None
        if self._sftp is not None:
            try:
                self._sftp.close()
            except Exception:  # Skip coverage.
                pass
            self._sftp = None

    def _normalize_path(self, path):
        path = self._expanduser(self._expandvars(path))
        if not self._pathlib.isabs(path):
            path = self._pathlib.join(self.cwd, path)
        return self._pathlib.normpath(path)

    def _setup_pathlib(self, platform):
        if platform == 'Windows':
            self._pathlib = ntpath
        else:
            self._pathlib = posixpath

    def _get_default_environment(self):
        try:
            platform = self.platform
        except OperationNotSupported:
            platform = 'Unknown'

        commands = []
        cmd = ('python -c "import sys, os; sys.stdout.write(\'\\n\'.join(['
               '\'%s=%s\' % (k, v) for k, v in os.environ.items()]))"')
        commands.append(self.execute(cmd))
        if platform in ['Windows', 'Unknown']:
            commands.append(self.execute('SET'))
        elif platform in ['Mac OS', 'Linux', 'Unknown']:
            commands.append(self.execute('env'))
        for command in commands:
            if command.wait(timeout=5.0) and command.exit_status == 0:
                data = command.stdout.read().decode('utf-8')
                env = {}
                for line in data.split('\n'):
                    match = _ENV_REGEX.match(line)
                    if match:
                        key, value = match.groups()
                        env[key] = value
                return env
            else:
                command.cancel()
        return {}

    def _expanduser(self, path):
        """
        :param str path: Path to expand the home directory with.
        :return: Result of calling os.path.expanduser with the separator.
        """
        sep = self._pathlib.sep
        if not path.startswith('~'):
            return path
        i = path.find(sep, 1)
        if i < 0:
            i = len(path)
        userhome = self.home.rstrip(sep)
        return (userhome + path[i:]) or sep


def _normalize_local_path(path):
    path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    return os.path.normpath(path)
