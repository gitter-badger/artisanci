import subprocess
from .base_command import BaseCommand
from ..exceptions import CommandClosedException

__all__ = [
    'BaseLocalCommand'
]


class BaseLocalCommand(BaseCommand):
    def __init__(self, worker, command, environment=None):
        super(BaseLocalCommand, self).__init__(worker, command, environment)
        self._proc = self._create_subprocess()

    def signal(self, signal):
        if self._proc is not None:
            self._proc.send_signal(signal)
        else:
            raise CommandClosedException(self.command)

    def cancel(self):
        if self._cancelled:
            raise CommandClosedException(self.command)
        try:
            self._proc.kill()
        except Exception:  # Skip coverage.
            pass
        self._proc = None
        self._cancelled = True

    def _create_subprocess(self):
        self._is_shell = True if not isinstance(self.command, list) else False
        return subprocess.Popen(self.command,
                                shell=self._is_shell,
                                cwd=self.worker.cwd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.environment)
