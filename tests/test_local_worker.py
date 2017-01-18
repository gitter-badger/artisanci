import os
import sys
import time
import unittest
from artisan import (LocalWorker,
                     LocalCommand)


def _safe_close(worker):
    try:
        worker.close()
    except Exception:
        pass


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


class TestLocalWorker(unittest.TestCase):
    def test_execute_command_type(self):
        worker = LocalWorker()
        self.assertIsInstance(worker.execute('Hello'), LocalCommand)

    def test_execute_async(self):
        worker = LocalWorker()
        start_time = time.time()
        worker.execute("sleep 1")
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)

    def test_execute_in_parallel(self):
        commands = []
        worker = LocalWorker()
        start_time = time.time()
        for _ in range(3):
            commands.append(worker.execute(sys.executable + " -c \"import time; time.sleep(1.0)\""))
        for command in commands:
            command.wait(timeout=1.5)
        end_time = time.time()
        for command in commands:
            self.assertEqual(command.exit_status, 0)
        self.assertLessEqual(end_time - start_time, 3.0)

    def test_execute_many_commands(self):
        commands = []
        worker = LocalWorker()
        for _ in range(10):
            commands.append(worker.execute(sys.executable + " -c \"import time; time.sleep(1.0)\""))
        for command in commands:
            command.wait(timeout=1.5)
        for command in commands:
            self.assertEqual(command.exit_status, 0)

    def test_execute_supply_environment(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE"})
        command.wait(1.0)
        self.assertEqual(command.stdout.read(), b'VARIABLE')

    def test_execute_override_environment(self):
        worker = LocalWorker()
        worker.environment["ENVIRONMENT"] = "VARIABLE1"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE2"})
        command.wait(1.0)
        self.assertEqual(command.stdout.read(), b'VARIABLE2')

    def test_stdout(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stdout.write('Hello')\"")
        command.wait(1.0)
        self.assertEqual(command.stdout.read(), b'Hello')
        self.assertEqual(command.stderr.read(), b'')
        self.assertEqual(command.exit_status, 0)

    def test_stderr(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stderr.write('Hello')\"")
        command.wait(1.0)
        self.assertEqual(command.stderr.read(), b'Hello')
        self.assertEqual(command.stdout.read(), b'')
        self.assertEqual(command.exit_status, 0)

    def test_exit_status(self):
        worker = LocalWorker()
        for exit_status in range(10):
            command = worker.execute(sys.executable + " -c \"import sys; sys.exit(%s)\"" % str(exit_status))
            command.wait(1.0)
            self.assertEqual(command.exit_status, exit_status)

    @unittest.skipIf(sys.version_info[0] == 2, 'Python 2.x subprocess.Popen.poll() blocks.')
    def test_exit_time(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.exit(2)\"")
        self.assertEqual(command.exit_status, None)
        time.sleep(1.0)
        self.assertEqual(command.exit_status, 2)

    @unittest.skipIf(sys.version_info[0] == 2, 'Python 2.x subprocess.Popen.poll() blocks.')
    def test_wait_timeout(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.5); sys.exit(2)\"")
        command.wait(0.1)
        self.assertIs(command.exit_status, None)
        command.wait(1.0)
        self.assertEqual(command.exit_status, 2)

    def test_cancel_command(self):
        worker = LocalWorker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(1.0); sys.stdout.write('Hello')\"")
        time.sleep(0.3)
        command.cancel()
        self.assertIs(command.exit_status, None)
        self.assertEqual(command.stdout.read(), b'')
        self.assertEqual(command.stderr.read(), b'')

    def test_close_worker(self):
        worker = LocalWorker()
        worker.close()
        self.assertTrue(worker.closed)

    def test_worker_already_closed(self):
        worker = LocalWorker()
        worker.close()
        self.assertRaises(ValueError, worker.close)

    def test_chdir(self):
        cwd = os.getcwd()
        worker = LocalWorker()
        worker.change_directory(cwd)
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.getcwd())\"")
        command.wait(1.0)
        self.assertEqual(cwd, str(command.stdout.read()).replace("\\\\", "\\").strip("b'\""))

    def test_chdir_same_directory(self):
        same_dir = os.getcwd()
        worker = LocalWorker()
        worker.change_directory(same_dir)
        worker.change_directory(".")
        self.assertEqual(same_dir, worker.cwd)

    def test_chdir_parent_directory(self):
        parent_dir = os.path.dirname(os.getcwd())
        worker = LocalWorker()
        worker.change_directory(os.getcwd())
        worker.change_directory("..")
        self.assertEqual(parent_dir, worker.cwd)

    def test_environ_get(self):
        worker = LocalWorker()
        for key, val in os.environ.items():
            self.assertIn(key, worker.environment)
            self.assertEqual(worker.environment[key], val)

    def test_environ_set(self):
        worker = LocalWorker()
        worker.environment["ENVIRONMENT"] = "VARIABLE"
        self.assertIn("ENVIRONMENT", worker.environment)
        self.assertEqual(worker.environment["ENVIRONMENT"], "VARIABLE")

    def test_environ_in_commands(self):
        worker = LocalWorker()
        worker.environment["ENVIRONMENT"] = "VARIABLE"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"")
        command.wait(1.0)
        self.assertEqual(command.stdout.read().strip(), b'VARIABLE')

    def test_listdir(self):
        expected = sorted(os.listdir("."))
        worker = LocalWorker()
        worker.change_directory(os.getcwd())
        self.assertEqual(sorted(worker.list_directory()), expected)

    def test_listdir_give_path(self):
        expected = sorted(os.listdir("."))
        worker = LocalWorker()
        self.assertEqual(sorted(worker.list_directory(path=os.getcwd())), expected)

    def test_open_file(self):
        worker = LocalWorker()
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="w") as f:
            f.write("Hello, world!")
        with worker.open_file("tmp", mode="r") as f:
            self.assertEqual(f.read(), "Hello, world!")

    def test_open_file_binary_mode(self):
        worker = LocalWorker()
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="wb") as f:
            f.write(b'Hello, world!')
        with worker.open_file("tmp", mode="rb") as f:
            self.assertEqual(f.read(), b'Hello, world!')

    def test_changing_cwd(self):
        worker = LocalWorker()
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir("..")
        self.assertEqual(worker.cwd, cwd)

    def test_put_file(self):
        worker = LocalWorker()
        self.addCleanup(_safe_remove, "tmp1")
        self.addCleanup(_safe_remove, "tmp2")
        _safe_remove("tmp1")
        _safe_remove("tmp2")
        with worker.open_file("tmp1", mode="w") as f:
            f.write("put")

        self.assertTrue(os.path.isfile("tmp1"))
        self.assertFalse(os.path.isfile("tmp2"))

        worker.put_file("tmp1", "tmp2")

        self.assertFalse(os.path.isfile("tmp1"))
        self.assertTrue(os.path.isfile("tmp2"))

        with worker.open_file("tmp2", mode="r") as f:
            self.assertEqual(f.read(), "put")

    def test_get_file(self):
        worker = LocalWorker()
        self.addCleanup(_safe_remove, "tmp1")
        self.addCleanup(_safe_remove, "tmp2")
        _safe_remove("tmp1")
        _safe_remove("tmp2")
        with worker.open_file("tmp1", mode="w") as f:
            f.write("get")

        self.assertTrue(os.path.isfile("tmp1"))
        self.assertFalse(os.path.isfile("tmp2"))

        worker.get_file("tmp1", "tmp2")

        self.assertFalse(os.path.isfile("tmp1"))
        self.assertTrue(os.path.isfile("tmp2"))

        with worker.open_file("tmp2", mode="r") as f:
            self.assertEqual(f.read(), "get")
