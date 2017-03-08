import os
import pickle
import tempfile
import unittest
from artisanci import LocalBuilder
from artisanci.builds import LocalBuild


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
        builder = LocalBuilder()

        delete_this = os.path.join(tempfile.gettempdir(), 'delete-this')
        open(delete_this, 'w+').close()
        self.addCleanup(_safe_remove, delete_this)

        job = LocalBuild(script=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'builds', 'simple.py'))
        job.environment['DELETE_THIS'] = delete_this

        builder.acquire()
        self.assertTrue(os.path.isfile(delete_this))
        builder.build_job(job)
        self.assertFalse(os.path.isfile(delete_this))
        builder.release()


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
