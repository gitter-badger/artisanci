import os
import sys
import pickle
import tempfile
import unittest
from artisanci import LocalBuilder
from artisanci.builds import LocalBuild
from artisanci.reporters import BasicCommandLineReporter


class TestLocalBuilder(unittest.TestCase):
    def test_builder_is_picklable(self):
        builder = LocalBuilder(builders=10)
        builder.acquire()
        builder.release()

        self.assertIsNotNone(builder._semaphore)

        # This test is to ensure that a Builder can be
        # passed through to a multiprocessing.Process instance.
        data = pickle.dumps(builder)
        builder2 = pickle.loads(data)

        self.assertIsInstance(builder2, LocalBuilder)
        self.assertEqual(builder.builders, builder2.builders)
        self.assertEqual(builder.python, builder2.python)

    def test_run_simple_job(self):
        builder = LocalBuilder(builders=1, python=sys.executable)

        delete_this = os.path.join(tempfile.gettempdir(), 'delete-this')
        open(delete_this, 'w+').close()
        self.addCleanup(_safe_remove, delete_this)

        build = LocalBuild(script=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'builds', 'simple.py'),
                           duration=5.0)
        build.add_watcher(BasicCommandLineReporter())
        build.environment['DELETE_THIS'] = delete_this

        self.assertTrue(os.path.isfile(delete_this))
        builder.execute_build(build)
        build.wait()
        self.assertFalse(os.path.isfile(delete_this))


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
