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


class SshWorker(BaseWorker):
    def __init__(self, host, username, port=22, environment=None,
                 add_policy=None, **kwargs):
        super(SshWorker, self).__init__(host, environment)

        if add_policy is None:
            add_policy = paramiko.AutoAddPolicy()
        assert isinstance(add_policy, paramiko.MissingHostKeyPolicy)

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(add_policy)
        try:
            self._ssh.connect(host, port, username, **kwargs)
        except paramiko.SSHException:
            raise WorkerNotAvailable()

        self._platform = None

    def execute(self, command, environment=None):
        return SshCommand(self, command, environment)

    @property
    def platform(self):
        if self._platform is not None:
            return self._platform
        c = self.execute('python -c "import platform, sys; sys.stdout.write(platform.system())"')
        if c.wait(timeout=5.0) and c.exit_status == 0:
            self._platform = c.stdout.read()
            return self._platform
        else:
            raise OperationNotSupported('platform', 'worker')

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
