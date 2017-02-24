import multiprocessing
from ..compat import Semaphore

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
    def __init__(self, python, builders):
        if not isinstance(python, str):
            raise TypeError('`python` must be of type `str`.')
        if not isinstance(builders, int):
            raise TypeError('`builders` must be of type `int`.')
        self.python = python
        self.builders = builders
        self._semaphore = None

        # This flag, if `True`, will allow the
        # builder to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is strongly discouraged.
        self.__is_secure = False

    def acquire(self):
        if self._semaphore is None:
            self._semaphore = Semaphore(self.builders)
        success = self._semaphore.acquire(blocking=False)
        return success

    def release(self):
        if self._semaphore is None:
            raise ValueError('Builder is not acquired.')
        self._semaphore.release()

    @property
    def is_secure(self):
        return self.__is_secure

    def run(self, job):
        proc = multiprocessing.Process(target=self._run, args=(job,))
        proc.start()
        proc.join()

    def execute(self, job):
        raise NotImplementedError()

    def setup(self, job):
        raise NotImplementedError()

    def teardown(self, job):
        raise NotImplementedError()

    def _run(self, job):
        try:
            self.setup(job)
            self.execute(job)
        finally:
            self.teardown(job)

    def __getstate__(self):
        __dict__ = self.__dict__.copy()
        __dict__['_semaphore'] = None
        return __dict__

    def __setstate__(self, state):
        self.__dict__.update(state)
