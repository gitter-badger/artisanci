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

""" Module with all implementations of
jobs that builders can execute. """

from .base_job import BaseJob
from .git_job import GitJob
from .local_job import LocalJob
from ..exceptions import ArtisanException

__all__ = [
    'BaseJob',
    'GitJob',
    'LocalJob',
    'job_factory'
]


def job_factory(type, name, script, **kwargs):
    if type == 'local':
        return LocalJob(name, script, **kwargs)
    elif type == 'git':
        return GitJob(name, script, **kwargs)
    else:
        raise ArtisanException('Unknown job type `%s`.' % type)
