from picklepipe import PicklePipe
from .base_command import BaseCommand

__all__ = [
    'RemoteCommand'
]


class RemoteCommand(BaseCommand):
    def __init__(self, pipe_id, worker, command, environment=None):
        super(RemoteCommand, self).__init__(worker, command, environment)
        self._pipe_id = pipe_id
        self._pipe = worker._pipe  # type: PicklePipe
        assert isinstance(self._pipe, PicklePipe)

        self._stdin = _RemoteStream(self, 'stdin')
        self._stdout = _RemoteStream(self, 'stdout')
        self._stderr = _RemoteStream(self, 'stderr')

    def wait(self, timeout=None, error_on_exit=False, error_on_timeout=False):
        kwargs = {'timeout': timeout,
                  'error_on_exit': error_on_exit,
                  'error_on_timeout': error_on_timeout}
        return send_and_recv(self._pipe, (self._pipe_id, 'wait', [], kwargs))

    def signal(self, signal):
        send_and_recv(self._pipe, (self._pipe_id, 'signal', [signal], {}))

    @property
    def exit_status(self):
        return send_and_recv(self._pipe, (self._pipe_id, '__getattr__',
                                          ['exit_status'], {}))

    @property
    def pid(self):
        return send_and_recv(self._pipe, (self._pipe_id, '__getattr__',
                                          ['pid'], {}))

    @property
    def is_shell(self):
        return send_and_recv(self._pipe, (self._pipe_id, '__getattr__',
                                          ['is_shell'], {}))

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    def cancel(self):
        self._cancelled = True
        send_and_recv(self._pipe, (self._pipe_id, 'cancel', [], {}))


class _RemoteStream(object):
    def __init__(self, command, stream):
        assert isinstance(command, RemoteCommand)
        self._command = command
        self._stream = stream

    def read(self, n=None):
        return send_and_recv(self._command._pipe, (self._command._pipe_id,
                                                   '_read_%s' % self._stream,
                                                   [n], {}))

    def write(self, data):
        return send_and_recv(self._command._pipe, (self._command._pipe_id,
                                                   '_write_%s' % self._stream,
                                                   [data], {}))


def send_and_recv(pipe, data):
    assert isinstance(pipe, PicklePipe)
    pipe.send_object(data)
    resp = pipe.recv_object(timeout=5.0)
    if isinstance(resp, BaseException):
        raise resp
    return resp
