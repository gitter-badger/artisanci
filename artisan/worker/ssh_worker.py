import functools
import re
import paramiko
from .base_worker import BaseWorker
from ..command import SshCommand
from ..exceptions import (OperationNotSupported,
                          WorkerNotAvailable)

__all__ = [
    'SshWorker'
]

_ENV_REGEX = re.compile('^([^=]+)=(.*)$')


def requires_sftp(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if self._sftp is None:
            raise OperationNotSupported(f.__name__, 'worker')
        return f(self, *args, **kwargs)
    return wrapper


class SshWorker(BaseWorker):
    def __init__(self, host, username, port=22, environment=None,
                 add_policy=None, **kwargs):

        if add_policy is None:
            add_policy = paramiko.AutoAddPolicy()
        assert isinstance(add_policy, paramiko.MissingHostKeyPolicy)

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(add_policy)
        try:
            self._ssh.connect(host, port, username, **kwargs)
        except paramiko.SSHException:
            raise WorkerNotAvailable()

        # This value is a fall-back if the home directory can't be found.
        self._start_dir = None
        try:
            self._sftp = self._ssh.open_sftp()
            self._start_dir = self._sftp.getcwd()
        except paramiko.SSHException:
            self._sftp = None  # type: paramiko.SFTPClient

        self._hostname = None
        self._platform = None
        self._home = None

        super(SshWorker, self).__init__(host, environment)

    def execute(self, command, environment=None):
        return SshCommand(self, command, environment)

    @requires_sftp
    def change_directory(self, path):
        self._sftp.chdir(path)

    @property
    @requires_sftp
    def cwd(self):
        return self._sftp.getcwd()

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

    @requires_sftp
    def remove_file(self, path):
        self._sftp.remove(path)

    @requires_sftp
    def remove_directory(self, path):
        self._sftp.rmdir(path)

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
