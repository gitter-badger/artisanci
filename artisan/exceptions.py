"""
All exceptions that are used within Artisan
are defined in this module.
"""
__all__ = [
    'JobFailureException',
    'WorkerLostException',
    'JobCancelledException',
    'JobErrorException',
    'JobTimeoutException',
    'CommandTimeoutException',
    'CommandExitStatusException',
    'OperationNotSupported'
]


class JobFailureException(Exception):
    """ Exception which would cause a Job to
    fail. Includes a `cause` which is to be
    displayed for users. """
    def __init__(self, cause=''):
        self.cause = cause
        super(JobFailureException, self).__init__()

    def __repr__(self):
        return '<JobFailureException cause=%s>' % self.cause


class WorkerLostException(JobFailureException):
    """ Exception for when during a Job a
    worker becomes unavailable unexpectedly
    or disconnects in the case of an SshWorker. """
    pass


class JobCancelledException(JobFailureException):
    """ Exception for when a Job is cancelled
    by some external force.  Usually this is
    by a user manually cancelling a Job."""
    pass


class JobErrorException(JobFailureException):
    """ If an Exception that is not caught occurs
    during a Job then this exception is raised
    with that exception attached. """
    def __init__(self, exception=None):
        self.exception = exception
        super(JobErrorException, self).__init__(
            'Exception occurred: %s' % str(exception))


class JobTimeoutException(JobFailureException):
    """ General exception for when an operation during the
    execution of a job times out such as a lock, barrier, etc. """
    def __init__(self, action='', timeout=0.0):
        super(JobTimeoutException, self).__init__(
            '%s in less than %s seconds' % (action, timeout))


class CommandTimeoutException(JobTimeoutException):
    """ Exception for calling :meth:`artisan.BaseCommand.wait` with
    ``error_on_timeout`` parameter equal to True and the command times out. """
    def __init__(self, command='', timeout=0.0):
        super(CommandTimeoutException, self).__init__(
            'Command `%s` did not exit' % command, timeout)


class CommandExitStatusException(JobFailureException):
    """ Exception for calling :meth:`artisan.BaseCommand.wait` with
    ``error_on_eixt`` equal to True and the command exits with
    a non-zero exit status."""
    def __init__(self, command='', exit_status=0):
        super(CommandExitStatusException, self).__init__(
            'Command `%s` exited with a non-zero exit status `%d`' % (command,
                                                                      exit_status))
        self.exit_status = exit_status
        
        
class OperationNotSupported(JobFailureException):
    """ The current operation is not supported on this worker. """
    def __init__(self, command, entity):
        super(OperationNotSupported, self).__init__(
            'The operation `%s` is not supported by this `%s`.' % (command, entity))
