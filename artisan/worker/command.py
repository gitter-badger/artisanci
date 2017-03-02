""" Defines the interface for a command resulting from BaseWorker.execute() """

import io
import subprocess
import threading
import time
from artisan.compat import monotonic
from artisan.exceptions import ArtisanException

__copyright__ = """
          Copyright (c) 2017 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""

__all__ = [
    'Command'
]

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty


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


class Command(object):
    """ Interface for commands executed by :class:`artisan.BaseWorker`.
    An instance of this must be returned from :meth:`artisan.BaseWorker.execute`"""
    def __init__(self, worker, command, environment=None, stdin=b'', merge_stderr=False):
        """
        Create an BaseCommand instance.

        :param str command: Command to execute on the worker.
        """
        self.worker = worker
        self.command = command
        self.environment = self._apply_minimum_environment(environment)

        self._is_shell = False
        self._proc = self._create_subprocess(stdin)

        self._exit_status = None
        self._stdout = b''
        self._stderr = b''
        self._merge_stderr = merge_stderr

        # Create the two monitoring threads.
        self._queue_threads = [_QueueThread(self._proc.stdout),
                               _QueueThread(self._proc.stderr)]
        self._queue_stdout = self._queue_threads[0].queue
        self._queue_stderr = self._queue_threads[1].queue
        for thread in self._queue_threads:
            thread.start()

    @property
    def is_shell(self):
        """
        Boolean value whether the command is being run as
        a shell or directly as a command.

         .. note::

            If this value is not True then the :py:attr:`artisan.BaseCommand.pid`
            property will not be accurate, the pid will be that of the shell.
        """
        return self._is_shell

    @property
    def stderr(self):
        """
        File-like object used for streaming a commands stderr.
        """
        self._check_exit()
        return self._stderr

    @property
    def stdout(self):
        """
        File-like object used for streaming a commands stdout.
        """
        self._check_exit()
        return self._stdout

    @property
    def exit_status(self):
        """
        Current exit status of the command.

        :returns: Exit status of the command as an `int` or None if not complete.
        """
        self._check_exit()
        return self._exit_status

    def _wait(self, timeout=None, error_on_exit=False, error_on_timeout=False):
        """
        Wait for the command to complete.
        Commands should always have this method called
        before trying to use any other property.

        :param float timeout: Number of seconds to wait before timing out.
        :param bool error_on_exit:
            If True will raise a :class:`artisan.CommandExitStatusException` if
            the command exits with a non-zero exit status.
        :param bool error_on_timeout:
            If True will raise a :class:`artisan.CommandTimeoutException` if
            the command times out while waiting for it to complete.
        :returns: True if the command exits, False otherwise.
        """
        start_time = monotonic()
        current_time = start_time
        not_complete = self._is_not_complete()
        if not not_complete:
            return True
        timed_out = False
        while self._is_not_complete():
            self._read_all(0.5 if timeout is None else min(0.5, current_time - start_time))
            if timeout is not None:
                current_time = monotonic()
                if current_time - start_time > timeout:
                    timed_out = True
                    break
        if self._is_not_complete() and timed_out and error_on_timeout:
            raise ArtisanException('The command `%s` failed to complete in '
                                   '`%.2f` seconds.' % (self.command, timeout))
        if not_complete and error_on_exit and self._exit_status not in [None, 0]:
            raise ArtisanException('The command `%s` exited with a status '
                                   'code of `%d`.' % (self.command, self._exit_status))
        return not self._is_not_complete()

    def _apply_minimum_environment(self, environment):
        """ Modifies the environment that will be passed
        to the command to have the minimum that is required
        for most commands to run successfully. """
        if environment is None:
            environment = self.worker.environment.copy()

        # PATH should be in the environment to be able to find binaries.
        if 'PATH' not in environment and 'PATH' in self.worker.environment:
            environment['PATH'] = self.worker.environment['PATH']

        # Windows requires SYSTEMROOT environment variable to be set before executing.
        if ('SYSTEMROOT' in self.worker.environment and
                'SYSTEMROOM' not in self.worker.environment):
            environment['SYSTEMROOT'] = self.worker.environment['SYSTEMROOT']

        return environment

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
                    self.worker._notify_listeners('command_output', data.decode('utf-8'))
                    self._stdout += data
            except Empty:
                pass
            try:
                while True:
                    data = self._queue_stderr.get_nowait()
                    if self._merge_stderr:
                        self.worker._notify_listeners('command_output', data.decode('utf-8'))
                        self._stdout += data
                    else:
                        self.worker._notify_listeners('command_error', data.decode('utf-8'))
                        self._stderr += data
            except Empty:
                pass
            if timeout is not None and monotonic() - start_time > timeout:
                break
            # Suggest that the thread to give up its CPU.
            time.sleep(0.0)

    def _is_not_complete(self):
        return (self._exit_status is None or
                self._queue_stdout.qsize() > 0 or
                self._queue_stderr.qsize() > 0 or
                not self._queue_threads[0].stop or
                not self._queue_threads[1].stop)

    def _check_exit(self):
        if self._is_not_complete():
            self._read_all(0.0)

    def _create_subprocess(self, stdin):
        self._is_shell = True if not isinstance(self.command, list) else False
        popen = subprocess.Popen(self.command,
                                 shell=self._is_shell,
                                 cwd=self.worker.cwd,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=self.environment)
        if stdin:
            popen.stdin.write(stdin)
        return popen
