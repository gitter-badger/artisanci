import socket
import picklepipe

from .base_worker import BaseWorker
from ..command import RemoteCommand

__all__ = [
    'RemoteWorker'
]


class RemoteWorker(BaseWorker):
    def __init__(self, host, port, environment=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._pipe = picklepipe.PicklePipe(sock)
        super(RemoteWorker, self).__init__(sock.getpeername(), environment)

    def execute(self, command, environment=None):
        self._pipe.send_object((0, 'execute', [command], {'environment': environment}))
        pipe_id = self._pipe.recv_object()
        return RemoteCommand(pipe_id, self, command, environment)

    def stat_file(self, path, follow_symlinks=True):
        return self._send_and_recv('stat_file', path, follow_symlinks=follow_symlinks)

    def list_directory(self, path='.'):
        return self._send_and_recv('list_directory', path)

    def change_directory(self, path):
        self._send_and_recv('change_directory', path)

    def is_directory(self, path):
        return self._send_and_recv('is_directory', path)

    def is_file(self, path):
        return self._send_and_recv('is_file', path)

    def is_symlink(self, path):
        return self._send_and_recv('is_symlink', path)

    @property
    def home(self):
        return self._send_and_recv('__getattr__', 'home')

    @property
    def hostname(self):
        return self._send_and_recv('__getattr__', 'hostname')

    @property
    def platform(self):
        return self._send_and_recv('__getattr__', 'platform')

    @property
    def cwd(self):
        return self._send_and_recv('__getattr__', 'cwd')

    def _get_default_environment(self):
        return self._send_and_recv('_get_default_environment')

    def _send_and_recv(self, func, *args, **kwargs):
        self._pipe.send_object((0, func, args, kwargs))
        obj = self._pipe.recv_object()
        if isinstance(obj, BaseException):
            raise obj
        return obj

    def close(self):
        super(RemoteWorker, self).close()
        try:
            self._pipe.close()
        except Exception:  # Skip coverage.
            pass
