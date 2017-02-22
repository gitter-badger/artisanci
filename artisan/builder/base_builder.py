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
    'BaseBuilder'
]


class BaseBuilder(object):
    """ Interface for Executors which setup and teardown the
    environment that a worker executes a job inside of. """
    def __init__(self, python):
        self.python = python
        self.busy = False

        # This flag, if `True`, will allow the
        # builder to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is strongly discouraged.
        self.is_secure = False

    def run(self, job):
        try:
            self.busy = True
            self.setup(job)
            self.execute(job)
        finally:
            self.busy = False
            self.teardown(job)

    def execute(self, job):
        raise NotImplementedError()

    def setup(self, job):
        raise NotImplementedError()

    def teardown(self, job):
        raise NotImplementedError()
