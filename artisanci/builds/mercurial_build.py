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
    'MercurialBuild'
]


class MercurialBuild(BaseBuild):
    def __init__(self, script, duration, repo, branch, revision=None):
        super(MercurialBuild, self).__init__('mercurial', script, duration)

        self.repo = repo
        self.branch = branch
        self.revision = revision

    def fetch_project(self, worker):
        super(MercurialBuild, self).fetch_project(worker)
        worker.execute('hg --version')

        project = os.path.join(worker.cwd, 'hg')
        command = 'hg clone %s -b %s %s' % (self.repo,
                                            self.branch,
                                            project)
        if self.revision is not None:
            command += ' -r %s' % self.revision

        worker.execute(command)
        worker.chdir(project)

        if self.revision is None:
            revision = worker.execute('hg log -l 1 -b . -T "{rev}\n"')
            self.revision = revision.stdout.decode('utf-8').strip()

        worker.environment['ARTISAN_BUILD_TYPE'] = 'mercurial'
        worker.environment['ARTISAN_MERCURIAL_REPOSITORY'] = self.repo
        worker.environment['ARTISAN_MERCURIAL_BRANCH'] = self.branch
        worker.environment['ARTISAN_MERCURIAL_REVISION'] = self.revision

    def as_args(self):
        args = ['--type', 'mercurial',
                '--script', self.script,
                '--repo', self.repo,
                '--branch', self.branch]
        if self.revision is None:
            args.extend(['--commit', self.revision])
        return args
