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
    'LocalBuild'
]

_SKIP_FILE_NAMES = {'.git', '.tox'}


class LocalBuild(BaseBuild):
    def __init__(self, script, duration, path=None):
        if path is None:
            path = os.getcwd()
        super(LocalBuild, self).__init__('local', script, duration)

        self.path = path

    def fetch_project(self, worker):
        super(LocalBuild, self).fetch_project(worker)
        for fileobj in os.listdir(self.path):
            if fileobj not in _SKIP_FILE_NAMES:
                worker.copy(os.path.join(self.path, fileobj), self.working_dir)

    def as_args(self):
        return ['--type', 'local',
                '--script', self.script,
                '--path', self.path]
