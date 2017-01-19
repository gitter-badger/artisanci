import subprocess
from .base_command import BaseCommand

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

    def cancel(self):
        if self._cancelled:
            raise ValueError("Command is already cancelled.")
        try:
            self._proc.kill()
        except Exception:
            pass
        self._proc = None
        self._cancelled = True

    def _create_subprocess(self):
        self.is_shell = True if not isinstance(self.command, list) else False
        return subprocess.Popen(self.command,
                                shell=self.is_shell,
                                cwd=self.worker.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.environment)
