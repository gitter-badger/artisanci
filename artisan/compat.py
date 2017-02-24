"""Compatibility functions for Python 2.x and 3.x """

import os
import sys
import time

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
    'PY2',
    'PY3',
    'PY33',
    'PY34',
    'PY35',

    'follows_symlinks',
    'sched_yield',
    'monotonic',
    'Lock',
    'Semaphore',
    'RLock',
    'Condition',
    'cmp_to_key',
    'xrange'
]

# Python version checking.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY33 = sys.version_info >= (3, 3)
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)

if PY3:
    xrange = range
else:
    xrange = xrange

if PY33:
    _FOLLOWS_SYMLINKS = set()
    if hasattr(os, 'chmod') and os.chmod in os.supports_follow_symlinks:
        _FOLLOWS_SYMLINKS.add('os.chmod')
    if hasattr(os, 'chown') and os.chown in os.supports_follow_symlinks:
        _FOLLOWS_SYMLINKS.add('os.chown')

    def follows_symlinks(name):
        return name in _FOLLOWS_SYMLINKS
else:
    def follows_symlinks(_):
        return False


# Getting a monotonic clock.
try:
    from time import monotonic
except ImportError:
    try:
        from monotonic import monotonic
    except (RuntimeError, ImportError):
        from time import time as monotonic

# Getting synchronization primitives with timeout options.
if sys.version_info >= (3, 0, 0):
    from threading import Lock, Semaphore, RLock, Condition
else:
    import threading

    def _timeout_acquire(acquired, blocking=True, timeout=None, command='acquire'):
        """ Helper function for acquiring a Semaphore or Lock
        object that doesn't have a `timeout` parameter. """
        if timeout is not None and not isinstance(timeout, (int, float)):
            raise ValueError('`timeout` must either be a float or None.')
        if blocking:
            if timeout is None:
                return getattr(acquired, command)(blocking=True)
            else:
                start_time = monotonic()
                while True:
                    if getattr(acquired, command)(blocking=False):
                        return True

                    if monotonic() - start_time > timeout:
                        return False

                    # Tries to convince the CPU to yield to another thread
                    # so that we don't continuously spin in this section.
                    time.sleep(0.0)
        else:
            return getattr(acquired, command)(blocking=False)

    class _BaseLock(object):
        """ Lock that implements the Python 3.x functionality
        of having the timeout parameter available for acquire. """
        def __init__(self, lock):
            self._lock = lock

        def acquire(self, blocking=True, timeout=None):
            return _timeout_acquire(self._lock, blocking, timeout)

        def release(self):
            self._lock.release()

        def __enter__(self):
            self._lock.acquire()
            return self

        def __exit__(self, *_):
            self._lock.release()

    class Lock(_BaseLock):
        def __init__(self):
            super(Lock, self).__init__(threading.Lock())

    class RLock(_BaseLock):
        def __init__(self):
            super(RLock, self).__init__(threading.RLock())

    class Semaphore(object):
        """ Semaphore that implements the Python 3.x functionality
        of having the timeout parameter available for acquire. """
        def __init__(self, value):
            self._semaphore = threading.Semaphore(value)

        def acquire(self, blocking=True, timeout=None):
            return _timeout_acquire(self._semaphore, blocking, timeout)

        def release(self):
            self._semaphore.release()

    class Condition(object):
        def __init__(self):
            self._condition = threading.Condition()

        def acquire(self, blocking=True, timeout=None):
            return _timeout_acquire(self._condition, blocking, timeout)

        def wait(self, timeout=None):
            return _timeout_acquire(self._condition, timeout != 0.0, timeout, command='wait')

        def release(self):
            self._condition.release()

        def notify(self, n):
            self._condition.notify(n)

        def notify_all(self):
            self._condition.notify_all()

try:
    from functools import cmp_to_key
except ImportError:
    # This cmp_to_key implementation taken from the
    # Python 3.5 implementation of functools.cmp_to_key.
    # License: Python Software Foundation License
    def cmp_to_key(cmp):
        class K(object):
            __slots__ = ['obj']

            def __init__(self, obj, *_):
                self.obj = obj

            def __lt__(self, other):
                return cmp(self.obj, other.obj) < 0

            def __gt__(self, other):
                return cmp(self.obj, other.obj) > 0

            def __eq__(self, other):
                return cmp(self.obj, other.obj) == 0

            def __le__(self, other):
                return cmp(self.obj, other.obj) <= 0

            def __ge__(self, other):
                return cmp(self.obj, other.obj) >= 0

            def __ne__(self, other):
                return cmp(self.obj, other.obj) != 0

            def __hash__(self):
                raise TypeError('hash not implemented')

        return K

# os.sched_yield was added in Python 3.3.
if hasattr(os, 'sched_yield'):
    sched_yield = os.sched_yield
else:
    def sched_yield():
        time.sleep(0.0)
