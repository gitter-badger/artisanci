from .base_job import BaseJob

__all__ = [
    'LocalJob'
]


class LocalJob(BaseJob):
    def __init__(self, name, script, path):
        super(LocalJob, self).__init__(name, script, {'path': path})

    def setup(self, worker):
        super(LocalJob, self).setup(worker)
        worker.chdir(self.params['path'])
        worker.environment['ARTISAN_BUILD_TYPE'] = 'local'

    def as_args(self):
        return ['--type', 'local',
                '--script', self.script,
                '--name', self.name,
                '--path', self.params['path']]
