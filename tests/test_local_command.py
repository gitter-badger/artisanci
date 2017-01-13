import os
import sys
from ._support import TestCase, skipPython2, skipPython3

from artisan import LocalCommand


class _FakeLocalWorker(object):
    def __init__(self):
        self.environment = os.environ.copy()
        self.cwd = os.getcwd()


class TestLocalCommand(TestCase):
    def test_execute_async(self):
        with self.assertRunningTime(upper=1.0):
            LocalCommand(_FakeLocalWorker(), 'sleep 1')

    def test_execute_in_parallel(self):
        with self.assertRunningTime(upper=3.0):
            commands = []
            for _ in range(3):
                commands.append(LocalCommand(_FakeLocalWorker(),
                                             'sleep 1'))
            for command in commands:
                command.wait(timeout=1.5)
                self.assertEqual(command.exit_status, 0)

    def test_execute_supply_environment(self):
        command = LocalCommand(_FakeLocalWorker(),
                               sys.executable + ' -c "import os, sys; sys.stdout.write(os.environ[\'ENVIRONMENT\'])"',
                               environment={'ENVIRONMENT': 'VARIABLE'})
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)

        stdout = command.stdout.read()
        self.assertEqual(stdout, b'VARIABLE')

    def test_execute_override_environment(self):
        worker = _FakeLocalWorker()
        worker.environment['ENVIRONMENT'] = 'VARIABLE1'
        command = LocalCommand(worker,
                               sys.executable + ' -c "import os, sys; sys.stdout.write(os.environ[\'ENVIRONMENT\'])"',
                               environment={'ENVIRONMENT': 'VARIABLE2'})
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)

        stdout = command.stdout.read()
        self.assertEqual(stdout, b'VARIABLE2')

    def test_stdout(self):
        command = LocalCommand(_FakeLocalWorker(),
                               sys.executable + ' -c "import os, sys; sys.stdout.write(\'Hello\')"')
        command.wait(timeout=1.0)
        stdout = command.stdout.read()
        stderr = command.stderr.read()
        self.assertIsInstance(stdout, bytes)
        self.assertEqual(stdout, b'Hello')
        self.assertEqual(stderr, b'')
        self.assertEqual(command.exit_status, 0)

    def test_stderr(self):
        command = LocalCommand(_FakeLocalWorker(),
                               sys.executable + ' -c "import sys; sys.stderr.write(\'Hello\')"')
        command.wait(timeout=1.0)
        stdout = command.stdout.read()
        stderr = command.stderr.read()
        self.assertIsInstance(stderr, bytes)
        self.assertEqual(stderr, b'Hello')
        self.assertEqual(stdout, b'')
        self.assertEqual(command.exit_status, 0)

    def test_chunked_data_reading(self):
        if sys.version_info > (3, 0, 0):
            cmd = sys.executable + ' -c "import os, sys; sys.stdout.buffer.write(os.urandom(128))"'
        else:
            cmd = sys.executable + ' -c "import os, sys; sys.stdout.write(os.urandom(128))"'
        command = LocalCommand(_FakeLocalWorker(), cmd)
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0, command.stderr.read())

        chunk_size = 8
        for _ in range(int(128 / chunk_size)):
            chunk = command.stdout.read(chunk_size=chunk_size)
            self.assertLen(chunk, chunk_size)
            self.assertIsInstance(chunk, bytes)

        self.assertLen(command.stdout.read(), 0)

    def test_streaming_data_reads(self):
        cmd = sys.executable + (' -c "import time, sys; f=sys.stdout.flush; sys.stdout.write(\'this\'); f(); '
                                'time.sleep(1.0); sys.stdout.write(\'is a\'); f(); time.sleep(1.0); '
                                'sys.stdout.write(\'test\'); f();"')
        command = LocalCommand(_FakeLocalWorker(), cmd)
        command.wait(timeout=1.0)
        self.assertIs(command.exit_status, None)
        self.assertEqual(command.stdout.read(), b'this')
        self.assertEqual(command.stdout.read(), b'is a')
        self.assertEqual(command.stdout.read(), b'test')
        self.assertEqual(command.exit_status, 0)
