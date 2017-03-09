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

""" Module for the base Builder interface. """

import multiprocessing
from ..compat import Semaphore
from ..watchable import Watchable

__all__ = [
    'BaseBuilder'
]


class BaseBuilder(Watchable):
    """ Interface for Executors which setup and teardown the
    environment that a worker executes a job inside of. """
    def __init__(self, python, builders):
        super(BaseBuilder, self).__init__()
        if not isinstance(python, str):
            raise TypeError('`python` must be of type `str`.')
        if not isinstance(builders, int):
            raise TypeError('`builders` must be of type `int`.')

        self.python = python
        self.builders = builders
        self._semaphore = None

    def acquire(self):
        if self._semaphore is None:
            self._semaphore = Semaphore(self.builders)
        success = self._semaphore.acquire(blocking=False)
        if success:
            self.notify_watchers('acquire', None)
        return success

    def release(self):
        if self._semaphore is None:
            raise ValueError('Builder is not acquired.')
        self._semaphore.release()
        self.notify_watchers('release', None)

    @property
    def is_secure(self):
        # This flag, if `True`, will allow the
        # builder to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is **strongly** discouraged.
        return False

    def execute_build(self, build):
        self.acquire()
        proc = multiprocessing.Process(target=self._build_target, args=(build,))
        proc.start()
        self.notify_watchers('execute_build', build)
        build._proc = proc
        self._build_target(build)
        build._builder = self

    def _build_target(self, build):
        raise NotImplementedError()

    def __getstate__(self):
        __dict__ = self.__dict__.copy()
        __dict__['_semaphore'] = None
        return __dict__

    def __setstate__(self, state):
        self.__dict__.update(state)
