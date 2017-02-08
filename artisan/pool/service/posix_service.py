import atexit
import os
import sys
from .base_service import BaseService

__all__ = [
    'PosixService'
]


class PosixService(BaseService):
    """ Interface for a service running on a POSIX platform. """
    def daemonize(self):
        # Uses the double-forking trick to
        # separate the child from the parent.
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

        os.chdir('/')
        os.setsid()
        os.umask(0)

        pid = os.fork()
        if pid > 0:
            sys.exit(0)

        sys.stdout.flush()
        sys.stderr.flush()
        stdin = open(self.stdin, 'r')
        stdout = open(self.stdout, 'a+')
        stderr = open(self.stderr, 'a+')
        os.dup2(stdin.fileno(), sys.stdin.fileno())
        os.dup2(stdout.fileno(), sys.stdout.fileno())
        os.dup2(stderr.fileno(), sys.stderr.fileno())

        atexit.register(self._delete_pid_file)
        pid = str(os.getpid())
        with open(self.pid_file, 'w+') as f:
            f.write(pid)
