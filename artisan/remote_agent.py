import socket
import threading
import selectors2 as selectors
from picklepipe import PicklePipe, PipeTimeout

from .worker import LocalWorker


class RemoteWorkerAgent(threading.Thread):
    def __init__(self, host, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self._sock.bind((host, port))
        self._sock.listen(512)

        self._selector = selectors.DefaultSelector()
        self._selector.register(self._sock, selectors.EVENT_READ)

        self._worker_pipes = {}

        super(RemoteWorkerAgent, self).__init__()

    def run(self):
        while self._sock is not None:
            for key, events in self._selector.select(timeout=1.0):
                sock = key.fileobj
                if sock is self._sock and selectors.EVENT_READ & events:
                    try:
                        client, _ = sock.accept()
                    except Exception:
                        continue
                    pipe = PicklePipe(client)
                    self._selector.register(pipe, selectors.EVENT_READ)
                    self._worker_pipes[pipe] = {0: LocalWorker()}
                else:
                    try:
                        pipe = sock
                        assert isinstance(pipe, PicklePipe)
                        try:
                            command = pipe.recv_object(timeout=1.0)
                            object_id = command[0]
                            obj = self._worker_pipes[pipe][object_id]
                        except PipeTimeout:
                            continue
                        try:
                            func, args, kwargs = command[1:]
                            if func == '__getattr__':
                                pipe.send_object(getattr(obj, args[0]))
                            else:
                                resp = getattr(obj, func)(*args, **kwargs)
                                if func == 'execute':
                                    next_id = max(self._worker_pipes[pipe].keys()) + 1
                                    self._worker_pipes[pipe][next_id] = resp
                                    pipe.send_object(next_id)
                                else:
                                    pipe.send_object(resp)
                        except Exception as e:
                            pipe.send_object(e)
                    except Exception:
                        self._selector.unregister(sock)
                        if sock in self._worker_pipes:
                            del self._worker_pipes[sock]
                        sock.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        if self._sock is None:
            return
        self._selector.close()
        self._selector = None

        self._sock.close()
        self._sock = None
