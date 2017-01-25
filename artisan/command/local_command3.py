""" LocalCommand implementation for Python 3.x+ """
import subprocess
from .base_local_command import BaseLocalCommand

__all__ = [
    'LocalCommand3'
]


class LocalCommand3(BaseLocalCommand):
    def __init__(self, worker, command, environment=None):
        super(LocalCommand3, self).__init__(worker, command, environment)
        self._proc = self._create_subprocess()

    @property
    def pid(self):
        if self._proc is None:
            return None
        return self._proc.pid

    def _read_all(self, timeout=0.0):
        if self._proc is None:
            return
        self._exit_status = self._proc.poll()
        stdin = b''
        if self._stdin.tell():
            self._stdin.seek(0, 0)
            stdin = self._stdin.read()
            self._stdin.truncate()
        try:
            stdout, stderr = self._proc.communicate(input=stdin,
                                                    timeout=timeout)
        except subprocess.TimeoutExpired:
            stdout, stderr = b'', b''
        if self._exit_status is None:
            if self._proc and self._proc.returncode is not None:
                self._exit_status = self._proc.returncode
        if stdout:
            self._write_data_to_stream(self._stdout, stdout)
        if stderr:
            self._write_data_to_stream(self._stderr, stderr)
