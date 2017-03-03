#           Copyright (c) 2017 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

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

        worker.run('git --version')

        tmp_dir = self.make_temporary_directory(worker)
        project_root = os.path.join(tmp_dir, 'git-project')
        worker.run('git clone --depth=50 --branch=%s %s %s' % (self.params['branch'],
                                                               self.params['repo'],
                                                               project_root))
        worker.chdir(project_root)
        worker.run('git checkout -qf %s' % self.params['commit'])

        if self.params['commit'] == 'HEAD':
            rev_parse = worker.run('git rev-parse HEAD')
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
