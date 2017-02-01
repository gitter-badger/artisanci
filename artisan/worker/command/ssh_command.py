""" Implementation of BaseCommand using SSH. """
import paramiko
from .base_command import BaseCommand
from artisan.compat import monotonic
from artisan.exceptions import CommandClosedException

__all__ = [
    'SshCommand'
]


class SshCommand(BaseCommand):
    def __init__(self, worker, command, environment):
        assert hasattr(worker, '_ssh'), 'Worker should have the `_ssh` attribute.'
        if isinstance(command, list):
            command = ' '.join(command)
        super(SshCommand, self).__init__(worker, command, environment)
        self._is_shell = True

        stdin, stdout, _ = worker._ssh.exec_command(command, environment=environment)
        self._channel = stdout.channel  # type: paramiko.Channel
        self._stdin_file = stdin

    def cancel(self):
        if self._cancelled:
            raise CommandClosedException(self.command)
        self._cancelled = True
        if self._channel is not None:
            try:
                self._channel.close()
            except Exception:  # Skip coverage.
                pass
            self._channel = None
        if self._stdin_file is not None:
            try:
                self._stdin_file.close()
            except Exception:  # Skip coverage.
                pass
            self._stdin_file = None

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
        self._stdin_file.write(self._stdin.read())
        self._stdin_file.flush()
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
