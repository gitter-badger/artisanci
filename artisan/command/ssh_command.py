import paramiko
from .base_command import BaseCommand
from ..compat import monotonic

__all__ = [
    'SshCommand'
]


class SshCommand(BaseCommand):
    def __init__(self, worker, command, environment):
        assert hasattr(worker, '_client'), 'Worker should have the `_client` attribute.'
        if isinstance(command, list):
            command = ' '.join(command)
        super(SshCommand, self).__init__(worker, command, environment)
        self.is_shell = True

        _, stdout, _ = worker._client.exec_command(command, environment=environment)
        self._channel = stdout.channel  # type: paramiko.Channel

    def cancel(self):
        if self._cancelled:
            raise ValueError('Command is already cancelled.')
        self._cancelled = True
        if self._channel is not None:
            try:
                self._channel.close()
            except Exception:  # Skip coverage.
                pass
            self._channel = None

    def _read_pipes(self, stdout, stderr):
        try:
            while self._channel.recv_ready():
                stdout.append(self._channel.recv(8192))
            while self._channel.recv_stderr_ready():
                stderr.append(self._channel.recv_stderr(8192))
        except paramiko.SSHException:
            pass

    def _read_all(self, timeout=0.0):
        if self._channel is None:
            return
        assert isinstance(self._channel, paramiko.Channel)
        if timeout is None:
            self._channel.setblocking(True)
        else:
            self._channel.setblocking(False)
        start_time = monotonic()
        stdout = []
        stderr = []
        try:
            while True:
                self._read_pipes(stdout, stderr)
                if self._channel.exit_status_ready():
                    self._exit_status = self._channel.recv_exit_status()
                    if self._exit_status is not None:
                        break
                if timeout is None or monotonic() - start_time > timeout:
                    break
        except paramiko.SSHException:
            pass

        # One last attempt to read remaining data from the channel.
        self._read_pipes(stdout, stderr)

        for chunk in stdout:
            self._write_data_to_stream(self._stdout, chunk)
        for chunk in stderr:
            self._write_data_to_stream(self._stderr, chunk)
