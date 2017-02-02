""" Definition of the BaseJob interface. """
import threading
from .exceptions import JobFailureException, JobErrorException

JOB_STATUS_PENDING = 'pending'
JOB_STATUS_RUNNING = 'running'
JOB_STATUS_SUCCESS = 'success'
JOB_STATUS_FAILURE = 'failure'
JOB_STATUS_ERROR = 'error'
JOB_STATUS_UNSTABLE = 'unstable'

_JOB_STATUSES_COMPLETED = set([JOB_STATUS_SUCCESS,
                               JOB_STATUS_FAILURE,
                               JOB_STATUS_UNSTABLE,
                               JOB_STATUS_ERROR])

__all__ = [
    'Job',

    'JOB_STATUS_FAILURE',
    'JOB_STATUS_ERROR',
    'JOB_STATUS_PENDING',
    'JOB_STATUS_SUCCESS',
    'JOB_STATUS_RUNNING',
    'JOB_STATUS_UNSTABLE'
]


class Job(threading.Thread):
    def __init__(self):
        self.worker = None
        self.status = JOB_STATUS_PENDING
        self.exception = None
        self.artifacts = {}

        self._callbacks = []

        super(Job, self).__init__()

    def run(self):
        """ Helper method that is used by scheduling
        jobs for a worker."""
        self.status = JOB_STATUS_RUNNING
        try:
            result = self.execute(self.worker)
            if result in _JOB_STATUSES_COMPLETED:
                self.status = result
            else:
                self.status = JOB_STATUS_SUCCESS
        except JobFailureException as e:
            self.exception = e
        except Exception as e:
            self.exception = JobErrorException(e)
        if self.exception is not None:
            self.status = JOB_STATUS_ERROR

        for func, args, kwargs in self._callbacks:
            func(self, *args, **kwargs)

    def add_callback(self, func, *args, **kwargs):
        """
        Add a function to call after the job is completed.
        Will be called immediately if the job is already completed.

        :param func: Function to call with the job as the only parameter.
        """
        if self.status in _JOB_STATUSES_COMPLETED:
            func(self, *args, **kwargs)
        else:
            self._callbacks.append((func, args, kwargs))

    def execute(self, worker):
        raise NotImplementedError()
