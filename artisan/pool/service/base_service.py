import os
import signal
import tempfile
import platform


class BaseService(object):
    """
    Interface for a daemon-like service process.
    """
    def __init__(self, pid_file, stdin=None, stdout=None, stderr=None):
        if stdin is None:
            stdin = os.devnull
        if stdout is None:
            stdout = os.devnull
        if stderr is None:
            stderr = os.devnull
        if not os.path.isabs(pid_file):
            if tempfile.gettempdir() is not None:
                tmp = tempfile.gettempdir()
            elif platform.system() == 'Windows':
                tmp = 'C:\\temp'
            else:
                tmp = '/tmp'
            pid_file = os.path.join(tmp, pid_file)

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pid_file = pid_file

    def start(self):
        """ Starts the service process. """
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
        except (OSError, IOError):
            pid = None
        if pid is not None:
            raise RuntimeError('PID file `%s` exists. Service is already running?' % self.pid_file)

        self.daemonize()
        self.run()

    def stop(self):
        """ Stops the service process from running. """
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
        except (OSError, IOError):
            pid = None
        if pid is None:
            raise RuntimeError('PID file `%s` does not exist. Service is not running?' % self.pid_file)
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            if e.errno == 3 and 'No such process' in str(e):
                self._delete_pid_file()
            else:
                raise

    def restart(self):
        try:
            self.stop()
        except RuntimeError:
            pass
        self.start()

    def daemonize(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def _delete_pid_file(self):
        try:
            os.remove(self.pid_file)
        except OSError:
            pass