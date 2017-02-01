import os
from artisan.worker import SshWorker
from artisan.worker.command import SshCommand
from .base_worker_testcase import _BaseWorkerTestCase


class TestSshWorker(_BaseWorkerTestCase):
    COMMAND_TYPE = SshCommand

    def make_worker(self):
        if 'ARTISAN_SSH_USERNAME' not in os.environ:
            self.skipTest('Could not find the `ARTISAN_SSH_USERNAME` in env.')
        return SshWorker('localhost',
                         os.environ['ARTISAN_SSH_USERNAME'],
                         password=os.environ['ARTISAN_SSH_PASSWORD'])
