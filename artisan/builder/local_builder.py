import sys
from .base_builder import BaseBuilder
from ..worker import Worker

__copyright__ = """
          Copyright (c) 2017 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""

__all__ = [
    'LocalBuilder'
]


class LocalBuilder(BaseBuilder):
    """ :class:`artisan.builder.BaseExecutor` implementation
    that uses the local machine to execute jobs using a
    :class:`artisan.Worker`.

     .. warning::
         This Executor is not safe for untrusted jobs.
         Consider using a different Executor for untrusted jobs.
    """
    def __init__(self, python=sys.executable):
        super(LocalBuilder, self).__init__(python)

    def setup(self, job):
        pass

    def execute(self, job):
        job.execute(Worker())

    def teardown(self, job):
        pass
