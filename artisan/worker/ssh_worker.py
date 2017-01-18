import paramiko
from .base_worker import BaseWorker
from ..command import SshCommand

__all__ = [
    'SshWorker'
]


class SshWorker(BaseWorker):
    def __init__(self, host, username, port=22, environment=None,
                 add_policy=None, **kwargs):
        super(SshWorker, self).__init__(host, environment)

        if add_policy is None:
            add_policy = paramiko.AutoAddPolicy()
        assert isinstance(add_policy, paramiko.MissingHostKeyPolicy)

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(add_policy)
        self._client.connect(host, port, username, **kwargs)

    def execute(self, command, environment=None):
        return SshCommand(self, command, environment)

    def _get_default_environment(self):
        return {}
