import multiprocessing
from .base_service import BaseService

__all__ = [
    'WindowsService'
]


class WindowsService(BaseService):
    """ Interface for a service running on a Windows platform. """
    def daemonize(self):
        daemon = multiprocessing.Process(target=self.run)
        daemon.daemon = True
        daemon.start()

        pid = str(daemon.pid)
        with open(self.pid_file, 'w+') as f:
            f.write(pid)

    def start(self):
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
        except (OSError, IOError):
            pid = None
        if pid is not None:
            raise RuntimeError('PID file `%s` exists. Service is already running?' % self.pid_file)

        self.daemonize()
