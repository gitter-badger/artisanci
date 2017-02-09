from .base_executor import BaseExecutor
from ..worker import LocalWorker

__all__ = [
    'LocalExecutor'
]


class LocalExecutor(BaseExecutor):
    """ :class:`artisan.executor.BaseExecutor` implementation
    that uses the local machine to execute jobs using a
    :class:`artisan.worker.LocalWorker`.

     .. warning::
         This Executor is not safe for untrusted jobs.
         Consider using a different Executor for untrusted jobs.
    """
    def setup(self):
        return LocalWorker()
