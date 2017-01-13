import six
import sys
import time

__all__ = [
    'skip',
    'skipUnless',
    'skipIf',
    'skipPython2',
    'skipPython3'
    'TestCase'
]

# Getting a proper `unittest` and `mock` modules.
if sys.version_info >= (2, 7):
    import unittest
    _UNITTEST = unittest
    if hasattr(_UNITTEST, 'mock'):
        _MOCK = _UNITTEST.mock
    else:
        import mock
        _MOCK = mock
else:
    import unittest2
    _UNITTEST = unittest2
    import mock
    _MOCK = mock


def safe_repr(obj, short=False):
    """ Implementation of safe_repr taken from unittest module. """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < 80:
        return result
    return result[:80] + ' [truncated]...'


# Getting a proper monotonic clock.
if hasattr(time, 'perf_counter'):
    monotonic = time.perf_counter
elif hasattr(time, 'monotonic'):
    monotonic = time.monotonic
else:
    try:
        from monotonic import monotonic
    except RuntimeError:
        monotonic = time.time


skipUnless = _UNITTEST.skipUnless
skipIf = _UNITTEST.skipIf
skip = _UNITTEST.skip
expectedFailure = _UNITTEST.expectedFailure


def _id(obj):
    return obj


def skipPython2():
    if six.PY2:
        return skip('Test is skipped on Python 2.x')
    return _id


def skipPython3():
    if six.PY3:
        return skip('Test is skipped on Python 3.x')
    return _id


# Implementation for the testcase with new helpers.
class _PatchContext(object):
    """ Helper object for tracking patched objects. """
    def __init__(self, obj, name, value):
        self._patched = False
        self._obj = obj
        self._name = name
        self._old_value = getattr(obj, name)
        setattr(self._obj, self._name, value)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.unpatch()

    def unpatch(self):
        if self._patched:
            self._patched = False
            setattr(self._obj, self._name, self._old_value)


class _TimerContext(object):
    """ Context manager for tracking the time that
    a section of code takes to execute. """
    def __init__(self, testcase, lower=None, upper=None, tolerance=None, msg=None):
        assert isinstance(testcase, TestCase)
        self.testcase = testcase
        self.lower = lower
        self.upper = upper
        self.tolerance = tolerance if tolerance is not None else 0.0
        self.start_time = None
        self.end_time = None
        self.msg = msg

    def __enter__(self):
        self.start_time = monotonic()
        return self

    def __exit__(self, *_):
        self.end_time = monotonic()
        total_time = self.end_time - self.start_time

        if self.lower is not None:
            msg = self.msg
            if msg is None:
                msg = 'Running time was shorter than %.3f seconds' % (self.lower - self.tolerance,)
            self.testcase.assertGreaterEqual(total_time, self.lower - self.tolerance, msg)
        if self.upper is not None:
            msg = self.msg
            if msg is None:
                msg = 'Running time was longer than %.3f seconds' % (self.upper + self.tolerance,)
            self.testcase.assertLessEqual(total_time, self.upper + self.tolerance, msg)


class TestCase(_UNITTEST.TestCase):
    """ Biased implementation of unittest.TestCase
    designed for Python 2.6+ with additional features. """
    def assertItemsEqual(self, first, second, msg=None):
        """ Don't know why this function had its name changed.
        The new name has nothing to do with sequence equality. """
        if hasattr(self, 'assertCountEqual'):
            self.assertCountEqual(first, second, msg)
        else:
            super(TestCase, self).assertItemsEqual(first, second, msg)

    def assertHasAttr(self, obj, name, msg=None):
        """ Asserts that the object has the attribute. """
        if msg is None:
            msg = '%s does not have the attribute %s' % (safe_repr(obj),
                                                         name)
        self.assertTrue(hasattr(obj, name), msg)

    def assertRunningTime(self, lower=None, upper=None, tolerance=None):
        """ Helper for timing a set of code. """
        return _TimerContext(self, lower=lower, upper=upper, tolerance=tolerance)

    def assertLen(self, obj, length, msg=None):
        """ Helper for asserting the length of an object. """
        self.assertHasAttr(obj, '__len__')
        if msg is None:
            msg = '%s is not length %s' % (safe_repr(obj),
                                           safe_repr(length))
        self.assertEqual(len(obj), length, msg)

    def assertTrue(self, expr, msg=None):
        """ Actually assert that the expression is `True` not just truthy. """
        self.assertIs(expr, True, msg)

    def assertFalse(self, expr, msg=None):
        """ Actually assert that the expression is `False` not just falsy. """
        self.assertIs(expr, False, msg)

    def assertTruthy(self, expr, msg=None):
        """ Equivalent to .assertIs(bool(expr), True) """
        super(TestCase, self).assertTrue(expr, msg)

    def assertFalsy(self, expr, msg=None):
        """ Equivalent to .assertIs(bool(expr), False) """
        super(TestCase, self).assertFalse(expr, msg)

    def assertStringType(self, obj, msg=None):
        """ Assert that the object is a string type for Python 2 or 3. """
        self.assertIsInstance(obj, six.string_types, msg)

    def assertIntegerType(self, obj, msg=None):
        """ Assert that the object is an integer type for Python 2 or 3. """
        self.assertIsInstance(obj, six.integer_types, msg)

    def patchObject(self, obj, name, value):
        """ Patch a value within an object with another value. """
        patch = _PatchContext(obj, name, value)
        self.addCleanup(patch.unpatch)
        return patch

    def mockObject(self, obj, name):
        """ Patch a value within an object with a Mock object. """
        mocked = _MOCK.Mock()
        self.patchObject(obj, name, mocked)
        return mocked
