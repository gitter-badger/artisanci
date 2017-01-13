from threading import Event, Lock
from ..compat import monotonic

__all__ = [
    'CommandByteStream'
]


def traceme(f):
    def tracer(*args, **kwargs):
        print(f.__name__, args, kwargs)
        ret = f(*args, **kwargs)
        print(ret)
        return ret
    return tracer


class CommandByteStream(object):
    def __init__(self, fd=None):
        super(CommandByteStream, self).__init__()
        self._fd = fd
        self._data = []
        self._closed = False

        self._ready_read = Event()
        self._ready_lock = Lock()

    def close(self):
        if not self._closed:
            self._closed = True
            self._ready_read.set()

    @property
    def closed(self):
        return self._closed

    @traceme
    def write(self, data):
        if self._closed:
            raise IOError()
        with self._ready_lock:
            self._data.append(data)
            if not self._ready_read.is_set():
                self._ready_read.set()
            return len(data)

    @traceme
    def read(self, chunk_size=None, timeout=None):
        if chunk_size is None:
            if not self._ready_read.wait(timeout=timeout):
                return b''
            with self._ready_lock:
                data = []  # Memory constant copy.
                for _ in range(len(self._data)):
                    data.append(self._data[0])
                    del self._data[0]

                self._ready_read.clear()
                return b''.join(data)
        else:
            data = b''
            start_time = monotonic()
            while len(data) < chunk_size:
                if not self._ready_read.wait(timeout=timeout):
                    break
                with self._ready_lock:
                    remaining = chunk_size - len(data)
                    if len(self._data[0]) > remaining:
                        self._data[0]
                    else:

                    if len(self._data) == 0:
                        self._ready_read.clear()
                if timeout is not None and monotonic() - start_time > timeout:
                    break
            return data

    def stream(self, chunk_size=None, timeout=None):
        while not self._closed:
            yield self.read(chunk_size, timeout)
