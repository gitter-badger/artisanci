import sys
from .base_builder import BaseBuilder
from ..worker import Worker

__all__ = [
    'LocalBuilder'
]


class LocalBuilder(BaseBuilder):
    """ :class:`artisan.builder.BaseExecutor` implementation
    that uses the local machine to execute jobs using a
    :class:`artisan.Worker`.

     .. warning::
         This Executor is not safe for untrusted jobs.
         Consider using a different Executor for untrusted jobs.
    """
    def __init__(self, python=sys.executable):
        super(LocalBuilder, self).__init__(python)

    def setup(self, job):
        pass

    def execute(self, job):
        job.execute(Worker())

    def teardown(self, job):
        pass
