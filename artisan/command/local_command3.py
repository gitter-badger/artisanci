""" LocalCommand implementation for Python 3.x+ """
import subprocess
from .base_local_command import BaseLocalCommand

__all__ = [
    "Local3Command"
]


class Local3Command(BaseLocalCommand):
    def __init__(self, worker, command, environment=None):
        super(Local3Command, self).__init__(worker, command, environment)
        self._proc = self._create_subprocess()

    @property
    def pid(self):
        if self._proc is None:
            return None
        return self._proc.pid

    def cancel(self):
        if self._cancelled:
            raise ValueError("Command is already cancelled.")
        self._proc.kill()
        self._proc = None
        self._cancelled = True

    def _read_all(self, timeout=0.0):
        if self._proc is None:
            return
        self._proc.poll()
        try:
            stdout, stderr = self._proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            stdout, stderr = b'', b''
        if self._exit_status is None:
            if self._proc and self._proc.returncode is not None:
                self._exit_status = self._proc.returncode
        if stdout:
            self._write_data_to_stream(self._stdout, stdout)
        if stderr:
            self._write_data_to_stream(self._stderr, stderr)
