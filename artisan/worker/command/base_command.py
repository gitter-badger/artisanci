import io
from artisan.compat import monotonic
from artisan.exceptions import (CommandTimeoutException,
                                CommandExitStatusException,
                                OperationNotSupported)


__all__ = [
    'BaseCommand'
]


class BaseCommand(object):
    """ Interface for commands executed by :class:`artisan.BaseWorker`.
    An instance of this must be returned from :meth:`artisan.BaseWorker.execute`"""
    def __init__(self, worker, command, environment=None):
        """
        Create an BaseCommand instance.

        :param str command: Command to execute on the worker.
        """
        self.worker = worker
        self.command = command
        self.environment = self._apply_minimum_environment(environment)
        self._is_shell = False

        self._cancelled = False
        self._exit_status = None
        self._stdout = io.BytesIO()
        self._stderr = io.BytesIO()
        self._stdin = io.BytesIO()

    @property
    def pid(self):
        """
        Process ID of the command.

         .. note::
            This is different from the sub-commands
            being run if using a shell rather than a
            list of command argv values. Check
            :py:attr:`artisan.BaseCommand.is_shell` before
            using this value if it needs to be accurate.
        """
        raise OperationNotSupported('pid', 'command')

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
    def stdin(self):
        """
        File-like object used for streaming a commands stdin.
        """
        return self._stdin

    @property
    def exit_status(self):
        """
        Current exit status of the command.

        :returns: Exit status of the command as an `int` or None if not complete.
        """
        self._check_exit()
        return self._exit_status

    def signal(self, signal):
        """
        Sends a signal to the process.

        :param int signal: Signal number to send to the child.
        """
        raise OperationNotSupported('signal()', 'command')

    def wait(self, timeout=None, error_on_exit=False, error_on_timeout=False):
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
        read_timeout = timeout
        not_complete = self._is_not_complete()
        if not not_complete:
            return True
        timed_out = False
        while self._is_not_complete():
            self._read_all(read_timeout)
            if timeout is not None:
                current_time = monotonic()
                if current_time - start_time > timeout:
                    timed_out = True
                    break
                read_timeout = max(0.0, (start_time + timeout) - current_time)
        if self._is_not_complete() and timed_out and error_on_timeout:
            raise CommandTimeoutException(self.command, timeout)
        if not_complete and error_on_exit and self._exit_status not in [None, 0]:
            raise CommandExitStatusException(self.command, self._exit_status)
        return not self._is_not_complete()

    def cancel(self):
        """ Cancel the command."""
        raise NotImplementedError()

    @property
    def cancelled(self):
        """ Boolean value whether the command
        has been manually cancelled. """
        return self._cancelled

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if not self._cancelled:
            try:
                self.cancel()
            except ValueError:  # Skip coverage.
                pass

    def __repr__(self):
        return '<%s command=`%s`>' % (type(self).__name__, self.command)

    def __str__(self):
        return self.__repr__()

    def _is_not_complete(self):
        return self._exit_status is None

    def _read_all(self, timeout=0.0):
        raise NotImplementedError()

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
        if self.worker.platform == 'Windows' and 'SYSTEMROOT' in self.worker.environment:
            environment['SYSTEMROOT'] = self.worker.environment['SYSTEMROOT']

        return environment

    def _check_exit(self):
        if self._is_not_complete():
            self._read_all(0.0)

    def _write_data_to_stream(self, stream, data):
        assert isinstance(stream, io.BytesIO)
        stream.write(data)
        stream.seek(-len(data), 1)

    def _read_stdout(self, n=None):
        return self.stdout.read(n)

    def _read_stderr(self, n=None):
        return self.stderr.read(n)

    def _write_stdin(self, data):
        self.stdin.write(data)
