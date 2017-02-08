import os
import signal
import socket
import stat
import sys
import tempfile
import time
import unittest
import platform
import six
from mock import patch

from artisan import (CommandExitStatusException,
                     CommandTimeoutException,
                     OperationNotSupported)
from artisan.worker import RemoteWorker, SshWorker

try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None


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

# Travis is really slow at signals for some reason. :/
_SIGNAL_TIMEOUT = 10.0 if 'TRAVIS' in os.environ else 3.0


class _BaseWorkerTestCase(unittest.TestCase):
    COMMAND_TYPE = None
    WORKER_TYPE = None
    
    def make_worker(self):
        raise NotImplementedError()

    def make_tmp_file(self):
        tmp = os.path.realpath(tempfile.mktemp())
        open(tmp, 'w+').close()
        self.addCleanup(_safe_remove, tmp)
        return tmp
    
    def test_execute_command_type(self):
        worker = self.make_worker()
        self.assertIsInstance(worker.execute('Hello'), self.COMMAND_TYPE)

    def test_execute_async(self):
        worker = self.make_worker()
        start_time = time.time()
        worker.execute("sleep 1")
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)

    def test_execute_in_parallel(self):
        commands = []
        worker = self.make_worker()
        start_time = time.time()
        for _ in range(3):
            commands.append(worker.execute(sys.executable + " -c \"import time; time.sleep(1.0)\""))
        for command in commands:
            command.wait(timeout=1.5)
        end_time = time.time()
        for command in commands:
            self.assertEqual(command.exit_status, 0)
        self.assertLessEqual(end_time - start_time, 3.0)

    def test_execute_supply_environment(self):
        worker = self.make_worker()

        if not worker.allow_environment_changes:
            self.skipTest('Worker will silently discard environment variables.')

        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE"})
        command.wait(1.0)
        self.assertEqual(command.stdout.read(), b'VARIABLE')

    def test_execute_override_environment(self):
        worker = self.make_worker()

        if not worker.allow_environment_changes:
            self.skipTest('Worker will silently discard environment variables.')

        worker.environment["ENVIRONMENT"] = "VARIABLE1"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE2"})
        command.wait(1.0)
        self.assertEqual(command.stdout.read(), b'VARIABLE2')

    def test_stdout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stdout.write('Hello')\"")
        command.wait(timeout=3.0, error_on_timeout=True)
        self.assertEqual(command.stdout.read(), b'Hello')
        self.assertEqual(command.stderr.read(), b'')
        self.assertEqual(command.exit_status, 0)

    def test_stderr(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stderr.write('Hello')\"")
        command.wait(timeout=3.0, error_on_timeout=True)
        self.assertEqual(command.stderr.read(), b'Hello')
        self.assertEqual(command.stdout.read(), b'')
        self.assertEqual(command.exit_status, 0)

    def test_stdin(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stdout.write(sys.stdin.read(13))\"")
        command.stdin.write(b'Hello, world!')
        command.wait(timeout=3.0, error_on_timeout=True)
        self.assertEqual(command.stdout.read(), b'Hello, world!')
        self.assertEqual(command.stderr.read(), b'')
        self.assertEqual(command.exit_status, 0)

    def test_exit_status(self):
        worker = self.make_worker()
        for exit_status in range(5):
            command = worker.execute(sys.executable + " -c \"import sys; sys.exit(%s)\"" % str(exit_status))
            command.wait(timeout=1.0)
            self.assertEqual(command.exit_status, exit_status)

    def test_exit_time(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.exit(2)\"")
        self.assertEqual(command.exit_status, None)
        time.sleep(1.0)
        self.assertEqual(command.exit_status, 2)

    def test_wait_timeout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.5); sys.exit(2)\"")
        command.wait(0.1)
        self.assertIs(command.exit_status, None)
        command.wait(1.0)
        self.assertEqual(command.exit_status, 2)

    def test_cancel_command(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(1.0); sys.stdout.write('Hello')\"")
        time.sleep(0.3)
        command.cancel()
        self.assertIs(command.exit_status, None)
        self.assertEqual(command.stdout.read(), b'')
        self.assertEqual(command.stderr.read(), b'')

    def test_execute_as_context_manager(self):
        worker = self.make_worker()
        with worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.stdout.write('Hello')\"") as c:
            c.wait(timeout=1.0)
            self.assertIs(c.exit_status, 0)
            self.assertEqual(c.stdout.read(), b'Hello')
            self.assertEqual(c.stderr.read(), b'')
        self.assertTrue(c.cancelled)

    def test_close_worker(self):
        worker = self.make_worker()
        worker.close()
        self.assertTrue(worker.closed)

    def test_worker_already_closed(self):
        worker = self.make_worker()
        worker.close()
        self.assertRaises(ValueError, worker.close)

    def test_chdir(self):
        cwd = os.getcwd()
        worker = self.make_worker()
        worker.change_directory(cwd)
        self.assertEqual(cwd, worker.cwd)

    def test_chdir_same_directory(self):
        same_dir = os.getcwd()
        worker = self.make_worker()
        worker.change_directory(same_dir)
        worker.change_directory(".")
        self.assertEqual(same_dir, worker.cwd)

    def test_chdir_parent_directory(self):
        parent_dir = os.path.dirname(os.getcwd())
        worker = self.make_worker()
        worker.change_directory(os.getcwd())
        worker.change_directory("..")
        self.assertEqual(parent_dir, worker.cwd)

    def test_expandvars_in_paths(self):
        old_dir = os.getcwd()
        basename = os.path.basename(os.getcwd())
        dirname = os.path.dirname(os.getcwd())

        worker = self.make_worker()
        worker.environment['ENVIRONMENT'] = basename
        worker.change_directory('..')
        worker.change_directory(os.path.join(dirname, '$ENVIRONMENT'))
        self.assertEqual(worker.cwd, old_dir)

    @unittest.skipUnless(platform.system() == 'Windows', 'This feature is only available on Windows.')
    def test_expandvars_in_paths_windows_variables(self):
        old_dir = os.getcwd()
        basename = os.path.basename(os.getcwd())
        dirname = os.path.dirname(os.getcwd())

        worker = self.make_worker()
        worker.environment['ENVIRONMENT'] = basename

        worker.change_directory('..')
        worker.change_directory(os.path.join(dirname, '%ENVIRONMENT%'))
        self.assertEqual(worker.cwd, old_dir)

    def test_expandvars_not_in_non_shell_commands(self):
        worker = self.make_worker()
        worker.environment['ENVIRONMENT'] = 'import sys; sys.exit(2)'
        command = worker.execute([sys.executable, '-c', '$ENVIRONMENT%'])
        if command.is_shell:
            self.skipTest('Command was shell by default.')
        command.wait(timeout=1.0)

        self.assertNotEqual(command.exit_status, 2)

    @unittest.skipUnless(platform.system() == 'Windows', 'This feature is only available on Windows.')
    def test_expandvars_not_in_non_shell_commands_windows(self):
        worker = self.make_worker()
        worker.environment['ENVIRONMENT'] = 'import sys; sys.exit(2)'
        command = worker.execute([sys.executable, '-c', '%ENVIRONMENT%'])
        if command.is_shell:
            self.skipTest('Command was shell by default.')
        command.wait(timeout=1.0)

        self.assertNotEqual(command.exit_status, 2)

    def test_home_directory(self):
        home = os.path.expanduser('~')
        worker = self.make_worker()
        self.assertEqual(worker.home, home)

    def test_hostname(self):
        worker = self.make_worker()
        self.assertEqual(worker.hostname, socket.gethostname())

    def test_stat(self):
        worker = self.make_worker()
        path = os.path.abspath(__file__)
        act = worker.stat_file(path)
        exp = os.stat(path)

        self.assertEqual(act.mode, exp.st_mode)
        self.assertEqual(act.inode, exp.st_ino)
        self.assertEqual(act.nlink, exp.st_nlink)

    @unittest.skipIf(platform.system() == 'Windows', 'Do not run on Windows.')
    def test_stat_follow_symlinks(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        os.symlink(source_path, link_path)
        self.addCleanup(_safe_remove, link_path)

        worker = self.make_worker()
        act = worker.stat_file(link_path, follow_symlinks=True)
        exp = os.stat(source_path)

        self.assertEqual(act.mode, exp.st_mode)
        self.assertEqual(act.inode, exp.st_ino)
        self.assertEqual(act.nlink, exp.st_nlink)

    @unittest.skipIf(platform.system() == 'Windows', 'Do not run on Windows.')
    def test_stat_dont_follow_symlinks(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        os.symlink(source_path, link_path)
        self.addCleanup(_safe_remove, link_path)

        worker = self.make_worker()
        act = worker.stat_file(link_path, follow_symlinks=False)
        not_exp = os.stat(source_path)
        exp = os.lstat(link_path)

        self.assertEqual(act.mode, exp.st_mode)
        self.assertEqual(act.inode, exp.st_ino)
        self.assertEqual(act.nlink, exp.st_nlink)
        self.assertNotEqual(act.inode, not_exp.st_ino)

    def test_change_mode_no_bit_flips(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        mode = os.stat(tmp).st_mode
        worker.change_file_mode(tmp, mode)
        self.assertEqual(os.stat(tmp).st_mode, mode)

    @unittest.skipIf(platform.system() == 'Windows', 'os.chmod does not have full function on Windows.')
    def test_change_mode(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        mode = os.stat(tmp).st_mode
        worker.change_file_mode(tmp, mode | stat.S_IXUSR)
        self.assertEqual(os.stat(tmp).st_mode, mode | stat.S_IXUSR)

    @unittest.skipIf(platform.system() == 'Windows', 'Symlinks and os.chmod not supported on Windows.')
    def test_change_mode_follow_symlinks(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        os.symlink(source_path, link_path)
        self.addCleanup(_safe_remove, link_path)
        st = os.stat(link_path)
        mode = st.st_mode

        worker = self.make_worker()
        worker.change_file_mode(link_path, mode | stat.S_IXUSR, follow_symlinks=True)
        st = os.stat(link_path)

        self.assertEqual(mode | stat.S_IXUSR, st.st_mode)

    @unittest.skipIf(platform.system() == 'Windows', 'Symlinks and os.chmod not supported on Windows.')
    def test_change_mode_dont_follow_symlinks(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        os.symlink(source_path, link_path)
        self.addCleanup(_safe_remove, link_path)
        st = os.lstat(link_path)
        mode = st.st_mode

        worker = self.make_worker()
        worker.change_file_mode(link_path, mode | stat.S_IXUSR, follow_symlinks=False)
        st = os.lstat(link_path)

        self.assertEqual(mode | stat.S_IXUSR, st.st_mode)

    @unittest.skipUnless(platform.system() == 'Windows', 'os.chmod is fully supported on non-Windows.')
    def test_change_mode_not_supported_on_windows(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        mode = os.stat(tmp).st_mode
        self.assertRaises(OperationNotSupported, worker.change_file_mode, tmp, mode | stat.S_IXUSR)

    @unittest.skipIf(platform.system() == 'Windows', 'os.chown() is not available on Windows.')
    def test_change_owner(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        gid = os.stat(tmp).st_gid

        with patch.object(os, 'chown') as mock:
            worker.change_file_owner(tmp, 127)

        if sys.version_info >= (3, 3) and os.chown in os.supports_follow_symlinks:
            mock.assert_called_once_with(tmp, 127, gid, follow_symlinks=True)
        else:
            mock.assert_called_once_with(tmp, 127, gid)

    def test_change_owner_with_no_chown(self):
        if hasattr(os, 'chown'):
            old_chown = os.chown
            delattr(os, 'chown')
            self.addCleanup(setattr, os, 'chown', old_chown)

        tmp = self.make_tmp_file()
        worker = self.make_worker()
        self.assertRaises(OperationNotSupported, worker.change_file_owner, tmp, 0)

    @unittest.skipUnless(platform.system() == 'Windows', 'os.chown is full supported on non-Windows.')
    def test_change_owner_not_supported_on_windows(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        self.assertRaises(OperationNotSupported, worker.change_file_owner, tmp, 0)

    @unittest.skipIf(platform.system() == 'Windows', 'os.chown() is not available on Windows.')
    def test_change_group(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        uid = os.stat(tmp).st_uid

        with patch.object(os, 'chown') as mock:
            worker.change_file_group(tmp, 127)

        if sys.version_info >= (3, 3) and os.chown in os.supports_follow_symlinks:
            mock.assert_called_once_with(tmp, uid, 127, follow_symlinks=True)
        else:
            mock.assert_called_once_with(tmp, uid, 127)

    def test_change_group_with_no_chown(self):
        if hasattr(os, 'chown'):
            old_chown = os.chown
            delattr(os, 'chown')
            self.addCleanup(setattr, os, 'chown', old_chown)

        tmp = self.make_tmp_file()
        worker = self.make_worker()
        self.assertRaises(OperationNotSupported, worker.change_file_group, tmp, 0)

    @unittest.skipUnless(platform.system() == 'Windows', 'os.chown is full supported on non-Windows.')
    def test_change_group_not_supported_on_windows(self):
        tmp = self.make_tmp_file()
        worker = self.make_worker()
        self.assertRaises(OperationNotSupported, worker.change_file_group, tmp, 0)

    def test_is_file(self):
        worker = self.make_worker()
        self.assertTrue(worker.is_file(os.path.abspath(__file__)))
        self.assertFalse(worker.is_file(os.path.dirname(os.path.abspath(__file__))))

    def test_is_directory(self):
        worker = self.make_worker()
        self.assertFalse(worker.is_directory(os.path.abspath(__file__)))
        self.assertTrue(worker.is_directory(os.path.dirname(os.path.abspath(__file__))))

    def test_environ_set(self):
        worker = self.make_worker()
        worker.environment["ENVIRONMENT"] = "VARIABLE"
        self.assertIn("ENVIRONMENT", worker.environment)
        self.assertEqual(worker.environment["ENVIRONMENT"], "VARIABLE")

    def test_environment_in_commands(self):
        worker = self.make_worker()

        if not worker.allow_environment_changes:
            self.skipTest('Worker will silently discard environment variables.')

        worker.environment["ENVIRONMENT"] = "VARIABLE"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"")
        command.wait(timeout=1.0)
        self.assertEqual(command.stdout.read().strip(), b'VARIABLE')

    def test_worker_del_environment(self):
        worker = self.make_worker()

        worker.environment['ENVIRONMENT'] = 'VARIABLE'
        self.assertIn('ENVIRONMENT', worker.environment)

        del worker.environment['ENVIRONMENT']
        self.assertNotIn('ENVIRONMENT', worker.environment)

        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"")
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 1)

    def test_listdir(self):
        expected = sorted(os.listdir("."))
        worker = self.make_worker()
        worker.change_directory(os.getcwd())
        self.assertEqual(sorted(worker.list_directory()), expected)

    def test_listdir_give_path(self):
        expected = sorted(os.listdir("."))
        worker = self.make_worker()
        self.assertEqual(sorted(worker.list_directory(path=os.getcwd())), expected)

    def test_open_file(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support open_file()')
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="w") as f:
            f.write("Hello, world!")
        with worker.open_file("tmp", mode="r") as f:
            self.assertEqual(f.read(), "Hello, world!")

    def test_open_file_binary_mode(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support open_file()')
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="wb") as f:
            f.write(b'Hello, world!')
        self.assertTrue(os.path.isfile('tmp'))
        with worker.open_file("tmp", mode="rb") as f:
            self.assertEqual(f.read(), b'Hello, world!')

    def test_open_file_exclusive_mode(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support open_file()')
        self.addCleanup(_safe_remove, "tmp")
        open('tmp', 'w+').close()
        self.assertTrue(os.path.isfile('tmp'))
        try:
            worker.open_file('tmp', 'x')
            self.fail('Did not raise an error.')
        except Exception:
            pass

    def test_open_file_exclusive_mode_is_writable(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support open_file()')
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="x") as f:
            f.write("Hello, world!")
        with worker.open_file("tmp", mode="r") as f:
            self.assertEqual(f.read(), "Hello, world!")

    def test_open_file_context_manager(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support open_file()')
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file('tmp', mode='w') as f:
            f.write('Hello, world!')
        with open('tmp', mode='r') as f:
            self.assertEqual(f.read(), 'Hello, world!')

    def test_put_file(self):
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support put_file()')

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
        worker = self.make_worker()
        if isinstance(worker, RemoteWorker):
            self.skipTest('RemoteWorkers currently don\'t support get_file()')
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

    def test_platform(self):
        worker = self.make_worker()
        self.assertEqual(worker.platform, platform.system())

    def test_worker_as_context_manager(self):
        with self.make_worker() as worker:
            self.assertIsInstance(worker, self.WORKER_TYPE)
            self.assertIs(worker.closed, False)
        self.assertIs(worker.closed, True)
    
    def test_execute_command_supply_environment(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import os, sys; sys.stdout.write(os.environ[\'ENVIRONMENT\'])"',
                                 environment={'ENVIRONMENT': 'VARIABLE'})
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)
    
        stdout = command.stdout.read()
        self.assertEqual(stdout, b'VARIABLE')
    
    def test_pid(self):
        worker = self.make_worker()
        command = worker.execute([sys.executable, '-c', 'import sys, os; sys.stdout.write(str(os.getpid()))'])
        if command.is_shell:
            self.skipTest('Command is a shell instance by default.')
    
        pid = command.pid
        command.wait(timeout=1.0)
        self.assertEqual(command.stdout.read(), str(pid).encode('utf-8'))
    
    def test_pid_after_cancel(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(3.0)"')
        command.cancel()
        self.assertIs(command.pid, None)

    # This signal actually works on Windows! :)
    def test_signal_terminate_exit_status(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(5.0)"')
        command.signal(signal.SIGTERM)
        command.wait(timeout=_SIGNAL_TIMEOUT, error_on_timeout=True)
        self.assertNotEqual(command.exit_status, 0)

    @unittest.skipIf(platform.system() == 'Windows', 'signal.SIGINT is not usable on Windows.')
    def test_signal_interrupt_exit_status(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(5.0)"')
        command.signal(signal.SIGINT)
        command.wait(timeout=_SIGNAL_TIMEOUT, error_on_timeout=True)
        self.assertNotEqual(command.exit_status, 0)

    @unittest.skipIf(platform.system() == 'Windows', 'signal.SIGFPE is not usable on Windows.')
    def test_signal_floating_point_exit_status(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(5.0)"')
        command.signal(signal.SIGFPE)
        command.wait(timeout=_SIGNAL_TIMEOUT, error_on_timeout=True)
        self.assertEqual(command.exit_status, -signal.SIGFPE)

    @unittest.skipIf(platform.system() == 'Windows', 'signal.alarm() is not usable on Windows.')
    def test_signal_alarm_exit_status(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import signal, time; signal.alarm(1) time.sleep(5.0)"')
        command.wait(timeout=_SIGNAL_TIMEOUT, error_on_timeout=True)
        self.assertNotEqual(command.exit_status, 0)
    
    def test_error_on_timeout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(3.0)"')
        self.assertRaises(CommandTimeoutException, command.wait, timeout=1.0, error_on_timeout=True)
    
    def test_error_on_exit(self):
        worker = self.make_worker()
        for i in range(5):
            command = worker.execute(sys.executable + ' -c "import time, sys; time.sleep(0.1); sys.exit(%d)"' % i)
            if i == 0:
                command.wait(timeout=1.0, error_on_exit=True)
            else:
                self.assertRaises(CommandExitStatusException, command.wait, timeout=1.0, error_on_exit=True)
            self.assertEqual(command.exit_status, i)

    def test_wait_returns_bool_false(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(1.0)"')
        self.assertIs(command.wait(timeout=0.1), False)
    
    def test_wait_returns_bool_true(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import time; time.sleep(0.1)"')
        self.assertIs(command.wait(timeout=1.0), True)
    
    def test_is_shell_true(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + ' -c "import sys, os; sys.exit(0)"')
        self.assertIs(command.is_shell, True)
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)

    def test_is_shell_false(self):
        worker = self.make_worker()
        if isinstance(worker, SshWorker):
            self.skipTest('SshCommand.is_shell is always True.')

        command = worker.execute([sys.executable, '-c', 'import sys, os; sys.exit(0)'])
        self.assertIs(command.is_shell, False)
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)

    def test_ssh_command_is_shell_always_true(self):
        worker = self.make_worker()
        if not isinstance(worker, SshWorker):
            self.skipTest('This test does not apply to non-SSH workers.')

        command = worker.execute([sys.executable, '-c', 'import sys, os; sys.exit(0)'])
        self.assertIs(command.is_shell, True)
        command.wait(timeout=1.0)
        self.assertEqual(command.exit_status, 0)
    
    def test_command_already_complete_wait_exit_immediately(self):
        worker = self.make_worker()
        command = worker.execute([sys.executable, '-c', 'import sys, os; sys.exit(0)'])
        self.assertIs(command.wait(timeout=1.0), True)
        self.assertIs(command.wait(timeout=1.0), True)

    @unittest.skipIf(platform.system() == 'Windows', 'Symlinks are not available on Windows.')
    def test_is_symlink(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        os.symlink(source_path, link_path)
        self.addCleanup(_safe_remove, link_path)

        worker = self.make_worker()
        self.assertTrue(worker.is_symlink(link_path))

    @unittest.skipIf(platform.system() == 'Windows', 'Symlinks are not available on Windows.')
    def test_create_symlink(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(test_dir, 'source')
        with open(source_path, 'w+') as f:
            f.write('source')
        self.addCleanup(_safe_remove, source_path)

        link_path = os.path.join(test_dir, 'symlink')
        self.addCleanup(_safe_remove, link_path)

        worker = self.make_worker()
        worker.create_symlink(source_path, link_path)

        self.assertTrue(worker.is_symlink(link_path))
        self.assertTrue(os.path.islink(link_path))

    def test_get_cpu_usage(self):
        worker = self.make_worker()

        user, system, idle = worker.get_cpu_usage()
        self.assertIsInstance(user, float)
        self.assertIsInstance(system, float)
        self.assertIsInstance(idle, float)

    def test_get_cpu_count(self):
        worker = self.make_worker()

        virtual_cpus = worker.get_cpu_count(physical=False)
        self.assertIsInstance(virtual_cpus, six.integer_types)
        self.assertGreater(virtual_cpus, 1)

        physical_cpus = worker.get_cpu_count(physical=True)
        self.assertIsInstance(physical_cpus, six.integer_types)
        self.assertLessEqual(physical_cpus, virtual_cpus)

    def test_get_memory_usage(self):
        worker = self.make_worker()

        used, free, total = worker.get_memory_usage()
        self.assertIsInstance(used, six.integer_types)
        self.assertIsInstance(free, six.integer_types)
        self.assertIsInstance(total, six.integer_types)
        self.assertEqual(used + free, total)

    def test_get_swap_usage(self):
        worker = self.make_worker()

        used, free, total = worker.get_swap_usage()
        self.assertIsInstance(used, six.integer_types)
        self.assertIsInstance(free, six.integer_types)
        self.assertIsInstance(total, six.integer_types)
        self.assertEqual(used + free, total)

    def test_get_disk_usage(self):
        worker = self.make_worker()

        used, free, total = worker.get_disk_usage()
        self.assertIsInstance(used, six.integer_types)
        self.assertIsInstance(free, six.integer_types)
        self.assertIsInstance(total, six.integer_types)
        self.assertLessEqual(used + free, total)

    def test_get_disk_partitions(self):
        worker = self.make_worker()

        parts = worker.get_disk_partitions()
        self.assertIsInstance(parts, list)

        for device, mount, fstype, opts in parts:
            self.assertIsInstance(device, str)
            self.assertIsInstance(device, str)
            self.assertIsInstance(fstype, str)
            self.assertIsInstance(opts, list)
            for opt in opts:
                self.assertIsInstance(opt, str)

    def test_get_physical_disk_partitions(self):
        worker = self.make_worker()

        virt = worker.get_disk_partitions()
        phys = worker.get_disk_partitions(physical=True)

        self.assertLessEqual(len(phys), len(virt))
