from artisan import RemoteWorker, RemoteWorkerAgent, RemoteCommand
from .base_worker_testcase import _BaseWorkerTestCase


REMOTE_AGENT_PORT = 12345


class TestRemoteWorker(_BaseWorkerTestCase):
    COMMAND_TYPE = RemoteCommand
    WORKER_TYPE = RemoteWorker

    def setUp(self):
        self._agent = RemoteWorkerAgent('0.0.0.0', REMOTE_AGENT_PORT)
        self._agent.start()

    def tearDown(self):
        self._agent.close()
        self._agent.join()
        self._agent = None

    def make_worker(self):
        return RemoteWorker('127.0.0.1', REMOTE_AGENT_PORT)
