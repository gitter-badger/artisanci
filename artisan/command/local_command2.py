""" LocalCommand implementation for Python 2.x """
import time
import threading
from Queue import Queue, Empty
from .base_local_command import BaseLocalCommand
from ..compat import monotonic

__all__ = [
    "Local2Command"
]


class _QueueThread(threading.Thread):
    """ Helper thread that turns a stream
    into chunks for a waitable queue. """
    def __init__(self, stream):
        super(_QueueThread, self).__init__()
        self._stream = stream
        self.queue = Queue()
        self.stop = False

    def run(self):
        try:
            for line in iter(self._stream.readline, b''):
                if self.stop:  # Skip coverage
                    break
                self.queue.put(line)
            self._stream.close()
        except Exception:  # Skip coverage
            pass
        self.stop = True


class Local2Command(BaseLocalCommand):
    def __init__(self, worker, command, environment=None):
        super(Local2Command, self).__init__(worker, command, environment)

        # Create the two monitoring threads.
        self._queue_threads = [_QueueThread(self._proc.stdout),
                               _QueueThread(self._proc.stderr)]
        self._queue_stdout = self._queue_threads[0].queue
        self._queue_stderr = self._queue_threads[1].queue
        for thread in self._queue_threads:
            thread.start()

    @property
    def pid(self):
        if self._proc is None:
            return None
        return self._proc.pid

    def cancel(self):
        if self._cancelled:
            raise ValueError("Command is already cancelled.")
        try:
            self._proc.kill()
        except Exception:
            pass
        for thread in self._queue_threads:
            thread.stop = True
        self._queue_threads = None
        self._proc = None
        self._cancelled = True

    def _read_all(self, timeout=0.001):
        if self._proc is None:
            return
        start_time = monotonic()
        while self._is_not_complete():
            if self._exit_status is None:
                self._exit_status = self._proc.poll()
            try:
                while True:
                    data = self._queue_stdout.get_nowait()
                    self._write_data_to_stream(self._stdout, data)
            except Empty:
                pass
            try:
                while True:
                    data = self._queue_stderr.get_nowait()
                    self._write_data_to_stream(self._stderr, data)
            except Empty:
                pass
            if timeout is not None and monotonic() - start_time <= timeout:
                break
            time.sleep(0.0)  # Suggest that the thread to give up its CPU.

    def _is_not_complete(self):
        return (self._exit_status is None or
                self._queue_stdout.qsize() > 0 or
                self._queue_stderr.qsize() > 0 or
                not self._queue_threads[0].stop or
                not self._queue_threads[1].stop)
