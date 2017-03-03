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

""" Module for a local Builder for running jobs on the local system. """

import sys
from .base_builder import BaseBuilder
from ..worker import Worker

__all__ = [
    'LocalBuilder'
]


class LocalBuilder(BaseBuilder):
    """ :class:`artisan.BaseBuilder` implementation
    that uses the local machine to execute jobs using a
    :class:`artisan.Worker`.

     .. warning::
         This builder is not safe for Community jobs.
    """
    def __init__(self, builders=1, python=sys.executable):
        super(LocalBuilder, self).__init__(builders=builders, python=python)

    def _build_job_target(self, job):
        worker = Worker()
        job.fetch_project(worker)
        job.setup_project(worker)
        job.execute_project(worker)
        job.cleanup_project(worker)
