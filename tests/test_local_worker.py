import os
from artisan import LocalCommand, LocalWorker
from .base_worker_testcase import _BaseWorkerTestCase


class TestLocalWorker(_BaseWorkerTestCase):
    COMMAND_TYPE = LocalCommand

    def make_worker(self):
        return LocalWorker()

    def test_environ_get(self):
        worker = self.make_worker()
        for key, val in os.environ.items():
            self.assertIn(key, worker.environment)
            self.assertEqual(worker.environment[key], val)
