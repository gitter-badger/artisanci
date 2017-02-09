from ..compat import Semaphore
from ..exceptions import WorkerNotAvailable
from ..job import JOB_STATUS_SUCCESS, JOB_STATUS_FAILURE, JOB_STATUS_RUNNING


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
        self._semaphore.acquire()
        self.workers += 1
        worker = None
        try:
            worker = self.setup()
            if worker is None:
                raise WorkerNotAvailable()
            job.run_install(worker)
            try:
                job.status = JOB_STATUS_RUNNING
                job.run_script(worker)
                job.status = JOB_STATUS_SUCCESS
            except Exception:
                job.status = JOB_STATUS_FAILURE
            try:
                job.run_after_complete(worker)
                if job.status == JOB_STATUS_FAILURE:
                    job.run_after_failure(worker)
                else:
                    job.run_after_success(worker)
            except Exception:
                pass
        finally:
            self._semaphore.release()
            self.workers -= 1
            self.teardown(worker)

    def setup(self):
        raise NotImplementedError()

    def teardown(self, worker):
        if worker is not None:
            worker.close()
