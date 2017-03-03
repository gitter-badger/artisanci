import os
from .base_job import BaseJob

__all__ = [
    'GitJob'
]


class GitJob(BaseJob):
    def __init__(self, name, script, repo, branch, commit=None):
        if commit is None:
            commit = 'HEAD'  # Get the latest if commit is None.

        params = {'repo': repo,
                  'branch': branch,
                  'commit': commit}
        super(GitJob, self).__init__(name, script, params)

    def setup(self, worker):
        super(GitJob, self).setup(worker)

        worker.execute('git --version')

        tmp_dir = self.make_temporary_directory(worker)
        project_root = os.path.join(tmp_dir, 'git-project')
        worker.execute('git clone --depth=50 --branch=%s %s %s' % (self.params['branch'],
                                                                   self.params['repo'],
                                                                   project_root))
        worker.chdir(project_root)
        worker.execute('git checkout -qf %s' % self.params['commit'])

        if self.params['commit'] == 'HEAD':
            rev_parse = worker.execute('git rev-parse HEAD')
            self.params['commit'] = rev_parse.stdout.decode('utf-8').strip()

        self.params['path'] = project_root

        worker.environment['ARTISAN_BUILD_TYPE'] = 'git'
        worker.environment['ARTISAN_GIT_REPOSITORY'] = self.params['repo']
        worker.environment['ARTISAN_GIT_BRANCH'] = self.params['branch']
        worker.environment['ARTISAN_GIT_COMMIT'] = self.params['commit']

    def as_args(self):
        return ['--type', 'git',
                '--script', self.script,
                '--name', self.name,
                '--repo', self.params['repo'],
                '--branch', self.params['branch'],
                '--commit', self.params['commit']]
