import errno
from artisan import RemoteWorkerAgent
from artisan.worker import RemoteWorker
from artisan.worker.command import RemoteCommand
from .base_worker_testcase import _BaseWorkerTestCase
from .port_helpers import find_unused_port


class TestRemoteWorker(_BaseWorkerTestCase):
    COMMAND_TYPE = RemoteCommand
    WORKER_TYPE = RemoteWorker

    def setUp(self):
        for _ in range(10):
            try:
                self._agent_port = find_unused_port()
                self._agent = RemoteWorkerAgent('0.0.0.0', self._agent_port)
                break
            except OSError as e:
                if e.errno == errno.EADDRINUSE:
                    continue
                raise
        else:
            self.skipTest('Could not create a RemoteWorkerAgent.')
        self._agent.start()
        super(TestRemoteWorker, self).setUp()

    def tearDown(self):
        self._agent.close()
        self._agent.join()
        self._agent = None

    def make_worker(self):
        return RemoteWorker('127.0.0.1', port=self._agent_port)
