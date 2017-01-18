from .worker import BaseWorker


class WorkerGroup(object):
    def __init__(self):
        self.workers = []

    def execute(self, command, environment=None):
        return self._worker_call('execute', command, environment)

    def _worker_call(self, func, *args, **kwargs):
        return [getattr(worker, func)(*args, **kwargs) for worker in self.workers]

