import socket
import picklepipe

from .base_worker import BaseWorker
from ..command import RemoteCommand

__all__ = [
    'RemoteWorker'
]


class RemoteWorker(BaseWorker):
    """ Implementation of the :class:`artisan.BaseWorker` interface
    that operates on another machine via ``picklepipe`` protocols. """
    def __init__(self, host, port, environment=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._pipe = picklepipe.PicklePipe(sock)
        super(RemoteWorker, self).__init__(sock.getpeername(), environment)

        self.environment = _RemoteEnvironment(self, self.environment)

    def execute(self, command, environment=None):
        if environment is None:
            environment = self.environment
        self._pipe.send_object((0, 'execute', [command], {'environment': environment.copy()}))
        pipe_id = self._pipe.recv_object()
        return RemoteCommand(pipe_id, self, command, environment)

    def change_file_mode(self, path, mode):
        self._send_and_recv('change_file_mode', path, mode)

    def change_file_owner(self, path, user_id):
        self._send_and_recv('change_file_owner', path, user_id)

    def change_file_group(self, path, group_id):
        self._send_and_recv('change_file_group', path, group_id)

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

    def put_file(self, local_path, remote_path):
        with open(local_path, 'rb') as f:
            self._send_and_recv('put_file', local_path, remote_path)
            data = f.read(4096)
            while data != b'':
                self._pipe.send_object((False, data))
                self._pipe.recv_object(timeout=5.0)
                data = f.read(4096)
            self._pipe.send_object((True, b''))
            self._pipe.recv_object(timeout=5.0)

    def get_file(self, remote_path, local_path):
        with open(local_path, 'wb') as f:
            f.truncate()
            self._send_and_recv('get_file', remote_path, local_path)
            while True:
                done, data = self._pipe.recv_object(timeout=5.0)
                f.write(data)
                self._pipe.send_object(None)
                if done:
                    break

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
        obj = self._pipe.recv_object(timeout=5.0)
        if isinstance(obj, BaseException):
            raise obj
        return obj

    def close(self):
        super(RemoteWorker, self).close()
        try:
            self._pipe.close()
        except Exception:  # Skip coverage.
            pass


class _RemoteEnvironment(dict):
    def __init__(self, worker, init):
        super(_RemoteEnvironment, self).__init__()
        assert isinstance(worker, RemoteWorker)
        self._worker = worker
        self._send_updates = False
        self.update(init)
        self._send_updates = True

    def __setitem__(self, key, value):
        if self._send_updates:
            self._worker._send_and_recv('_set_environment', key, value)
        super(_RemoteEnvironment, self).__setitem__(key, value)

    def __delitem__(self, key):
        if self._send_updates:
            self._worker._send_and_recv('_del_environment', key)
        super(_RemoteEnvironment, self).__delitem__(key)
