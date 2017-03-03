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
    'MercurialJob'
]


class MercurialJob(BaseJob):
    def __init__(self, name, script, repo, branch, commit):
        params = {'repo': repo,
                  'branch': branch,
                  'commit': commit}
        super(MercurialJob, self).__init__(name, script, params)

    def setup(self, worker):
        super(MercurialJob, self).setup(worker)

        worker.environment['ARTISAN_BUILD_TYPE'] = 'mercurial'
        worker.environment['ARTISAN_MERCURIAL_REPOSITORY'] = self.params['repo']
        worker.environment['ARTISAN_MERCURIAL_BRANCH'] = self.params['branch']
        worker.environment['ARTISAN_MERCURIAL_COMMIT'] = self.params['commit']

        tmp_dir = self.make_temporary_directory(worker)
        worker.run('hg clone %s -r %s' % (self.params['repo'], self.params['branch']))
        repository = os.path.join(tmp_dir, worker.list_directory()[0])
        worker.change_directory(repository)

    def as_args(self):
        return ['--type', 'mercurial',
                '--script', self.script,
                '--name', self.name,
                '--repo', self.params['repo'],
                '--branch', self.params['branch']]
