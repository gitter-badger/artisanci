""" Command implementation for Python 2.x """

#           Copyright (c) 2017 Seth Michael Larson
# _________________________________________________________________
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import threading
from .base_command_impl import BaseCommandImpl
from artisan.compat import monotonic, sched_yield

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

__all__ = [
    'Command2'
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


class Command2(BaseCommandImpl):
    def __init__(self, worker, command, environment=None):
        super(Command2, self).__init__(worker, command, environment)

        # Create the two monitoring threads.
        self._queue_threads = [_QueueThread(self._proc.stdout),
                               _QueueThread(self._proc.stderr)]
        self._queue_stdout = self._queue_threads[0].queue
        self._queue_stderr = self._queue_threads[1].queue
        for thread in self._queue_threads:
            thread.start()

    def cancel(self):
        super(Command2, self).cancel()
        for thread in self._queue_threads:
            thread.stop = True
        self._queue_threads = None

    def _read_all(self, timeout=0.001):
        if self._proc is None:
            return
        start_time = monotonic()
        while self._is_not_complete():
            if self._stdin.tell():
                self._stdin.seek(0, 0)
                data = self._stdin.read()
                self._proc.stdin.write(data)
                self._stdin.truncate(0)
            if self._exit_status is None:
                self._exit_status = self._proc.poll()
            try:
                while True:
                    data = self._queue_stdout.get_nowait()
                    self.worker.report.output_command(data.decode('utf-8'))
                    self._write_data_to_stream(self._stdout, data)
            except Empty:
                pass
            try:
                while True:
                    data = self._queue_stderr.get_nowait()
                    self.worker.report.output_command(data.decode('utf-8'), True)
                    self._write_data_to_stream(self._stderr, data)
            except Empty:
                pass
            if timeout is not None and monotonic() - start_time > timeout:
                break
            # Suggest that the thread to give up its CPU.
            sched_yield()

    def _is_not_complete(self):
        return (self._exit_status is None or
                self._queue_stdout.qsize() > 0 or
                self._queue_stderr.qsize() > 0 or
                not self._queue_threads[0].stop or
                not self._queue_threads[1].stop)
