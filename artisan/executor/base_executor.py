import time
from ..exceptions import WorkerNotAvailable

__all__ = [
    'BaseExecutor'
]


class BaseExecutor(object):
    """ Interface for Executors which maintain the environment for a worker
    to execute a job. Also handles the reporting of """
    def __init__(self, python):
        self.python = python

        # This flag, if `True`, will allow the
        # executor to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is strongly discouraged.
        self.is_secure = False

    def execute(self, job):
        worker = None
        try:
            worker = self.setup()
            if worker is None:
                raise WorkerNotAvailable()
            job.run_process(worker)

            # This is where the timer starts.
            start_time = time.time()

            # TODO: Hand off the job to the worker and execute!

            end_time = time.time()
            # This is where the timer ends.
        finally:
            self.teardown(worker)

    def run_artisan(self, job):
        raise NotImplementedError()

    def setup(self):
        raise NotImplementedError()

    def teardown(self, worker):
        if worker is not None:
            worker.close()
