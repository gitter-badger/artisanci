import os
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
    def __init__(self, report, python=sys.executable):
        super(LocalExecutor, self).__init__(report, python)

    def setup(self, job):
        pass

    def execute(self, job):
        self.report.set_state('setup')

        worker = Worker(self.report)


        error = None
        try:
            job.setup(worker)
            if hasattr(script, 'install'):
                self.report.set_state('install')
                script.install(worker)
            if hasattr(script, 'script'):
                self.report.set_state('script')
                script.script(worker)
            if hasattr(script, 'after_success'):
                self.report.set_state('after_success')
                script.after_success(worker)
        except Exception as e:
            error = e
            self.report.output_command('ERROR: %s %s' % (type(error).__name__, str(error)), True)
        if error is not None:
            try:
                if hasattr(script, 'after_failure'):
                    self.report.set_state('after_failure')
                    script.after_failure(worker)
            except Exception:
                pass
            self.report.build_failure()
            raise error
        else:
            self.report.build_success()
        job.cleanup()

    def teardown(self, job):
        pass
