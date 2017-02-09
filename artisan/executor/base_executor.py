import time
from ..compat import Semaphore
from ..exceptions import WorkerNotAvailable
from ..job import Job, JobStatus

__all__ = [
    'BaseExecutor'
]


class BaseExecutor(object):
    """ Interface for Executors which maintain the environment for a worker
    to execute a job. Also handles the reporting of """
    def __init__(self, workers=1):
        self.workers = workers
        self._semaphore = Semaphore(workers)

        # This flag, if `True`, will allow the
        # executor to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is strongly discouraged.
        self.is_secure = False

    def execute(self, job):
        assert isinstance(job, Job)
        self._semaphore.acquire()
        self.workers += 1
        worker = None
        try:
            worker = self.setup()
            if worker is None:
                raise WorkerNotAvailable()
            job.status = JobStatus.INSTALLING
            job.run_process(worker)

            # This is where the timer starts.
            start_time = time.time()

            # TODO: Hand off the job to the worker and execute!

            end_time = time.time()
            # This is where the timer ends.
        finally:
            self._semaphore.release()
            self.workers -= 1
            self.teardown(worker)

    def setup(self):
        raise NotImplementedError()

    def teardown(self, worker):
        if worker is not None:
            worker.close()
