import sys
from .base_executor import BaseExecutor
from ..worker import Worker

__all__ = [
    'LocalExecutor'
]


class LocalExecutor(BaseExecutor):
    """ :class:`artisan.executor.BaseExecutor` implementation
    that uses the local machine to execute jobs using a
    :class:`artisan.Worker`.

     .. warning::
         This Executor is not safe for untrusted jobs.
         Consider using a different Executor for untrusted jobs.
    """
    def __init__(self, python=sys.executable):
        super(LocalExecutor, self).__init__(python)

    def setup(self):
        return Worker()
