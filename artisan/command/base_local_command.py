import subprocess
from .base_command import BaseCommand


class BaseLocalCommand(BaseCommand):
    def __init__(self, worker, command, environment=None):
        super(BaseLocalCommand, self).__init__(worker, command, environment)
        self._proc = self._create_subprocess()

    def signal(self, signal):
        if self._proc is not None:
            self._proc.send_signal(signal)

    def _create_subprocess(self):
        return subprocess.Popen(self.command,
                                shell=True if not isinstance(self.command, list) else False,
                                cwd=self.worker.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.environment)
