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
from .base_build import BaseBuild

__all__ = [
    'GitBuild'
]


class GitBuild(BaseBuild):
    def __init__(self, script, repo, branch, commit=None):
        if commit is None:
            commit = 'HEAD'  # Get the latest if commit is None.

        super(GitBuild, self).__init__(script, 'git')

        self.repo = repo
        self.branch = branch
        self.commit = commit

    def fetch_project(self, worker):
        super(GitBuild, self).fetch_project(worker)
        worker.execute('git --version')

        project = os.path.join(worker.cwd, 'git')
        worker.execute('git clone --depth=50 --branch=%s %s %s' % (self.branch,
                                                                   self.repo,
                                                                   project))
        worker.chdir(project)
        worker.execute('git checkout -qf %s' % self.commit)

        if self.commit == 'HEAD':
            rev_parse = worker.execute('git rev-parse HEAD')
            self.commit = rev_parse.stdout.decode('utf-8').strip()

        worker.environment['ARTISAN_BUILD_TYPE'] = 'git'
        worker.environment['ARTISAN_GIT_REPOSITORY'] = self.repo
        worker.environment['ARTISAN_GIT_BRANCH'] = self.branch
        worker.environment['ARTISAN_GIT_COMMIT'] = self.commit

    def as_args(self):
        return ['--type', 'git',
                '--script', self.script,
                '--repo', self.repo,
                '--branch', self.branch,
                '--commit', self.commit]
