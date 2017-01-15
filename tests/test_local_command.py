import os
import sys
from ._support import TestCase

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

    def test_pid(self):
        command = LocalCommand(_FakeLocalWorker(),
                               [sys.executable, '-c', 'import sys, os; sys.stdout.write(str(os.getpid()))'])
        pid = command.pid
        command.wait(timeout=1.0)
        self.assertEqual(command.stdout.read(), b'%d' % pid)
