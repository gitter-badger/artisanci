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
    'LocalJob'
]


class LocalJob(BaseJob):
    def __init__(self, name, script, path=None):
        if path is None:
            path = os.getcwd()
        super(LocalJob, self).__init__(name, script)

        self.path = path

    def fetch_project(self, worker):
        super(LocalJob, self).fetch_project(worker)
        worker.chdir(self.path)

    def as_args(self):
        return ['--type', 'local',
                '--script', self.script,
                '--name', self.name,
                '--path', self.path]
