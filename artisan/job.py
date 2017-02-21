import os
import sys
import uuid
from .worker import Worker

__all__ = [
    'Job',
    'LocalJob',
    'GitJob'
]


class Job(object):
    def __init__(self, script, params):
        self.script = script
        self.params = params
        self.report = None
        self.labels = {}

        self._cleanup_calls = []

    def setup(self, worker):
        assert isinstance(worker, Worker)
        worker.add_listener(self.report)

        if 'ARTISAN_API_KEY' in os.environ:
            worker.environment['ARTISAN_API_KEY'] = os.environ['ARTISAN_API_KEY']

    def execute(self, worker):
        # Executing each part of the script.
        error = None
        script = None
        self.report.on_status_change('setup')
        try:
            self.setup(worker)

            # Importing the script module.
            script_path = self.script
            if os.path.isabs(self.script):
                script_path = os.path.join(worker.cwd, script_path)
            script_module = os.path.basename(script_path)
            if script_module.endswith('.py'):
                script_module = script_module[:-3]
            sys.path.insert(0, os.path.dirname(script_path))
            script = __import__(script_module)
            sys.path = sys.path[1:]

            # Set the build directory to the current directory.
            worker.environment['ARTISAN_BUILD_DIR'] = worker.cwd

            # Show all environment variables sorted.
            self.report.on_next_command('env')
            for key, value in sorted(worker.environment.items()):
                self.report.on_command_output('%s=%s%s' % (key, value, '\r\n' if worker.platform == 'Windows' else '\n'))

            if hasattr(script, 'install'):
                self.report.on_status_change('install')
                script.install(worker)
            if hasattr(script, 'script'):
                self.report.on_status_change('script')
                script.script(worker)
            if hasattr(script, 'after_success'):
                self.report.on_status_change('after_success')
                script.after_success(worker)
        except Exception as e:
            error = e
            self.report.on_command_error('ERROR: %s %s' % (type(error).__name__, str(error)))
        if error is not None:
            try:
                if hasattr(script, 'after_failure'):
                    self.report.set_state('after_failure')
                    script.after_failure(worker)
            except Exception:
                pass
        try:
            self.report.on_status_change('cleanup')
            self.cleanup(worker)
        except Exception:
            pass
        if error is not None:
            self.report.on_status_change('failure')
        else:
            self.report.on_status_change('success')

    def add_cleanup(self, func, *args, **kwargs):
        self._cleanup_calls.append((func, args, kwargs))

    def cleanup(self, worker):
        for func, args, kwargs in self._cleanup_calls:
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        worker.remove_listener(self.report)

    def make_temporary_directory(self, worker):
        assert isinstance(worker, Worker)
        worker.change_directory(worker.tmp)
        tmp_dir = uuid.uuid4().hex
        while worker.is_directory(tmp_dir):
            tmp_dir = uuid.uuid4().hex
        worker.create_directory(tmp_dir)
        worker.change_directory(tmp_dir)
        tmp_dir = worker.cwd
        self.add_cleanup(worker.remove_directory, tmp_dir)
        return tmp_dir

    def activate_python_virtualenv(self, worker):
        if worker.is_directory('.venv'):
            worker.remove_directory('.venv')
        worker.execute('virtualenv -p %s .venv' % sys.executable)
        if worker.platform == 'Windows':
            worker.environment['PATH'] = os.path.join(worker.cwd, '.venv', 'Scripts') + ';' + worker.environment.get('PATH', '')
        else:
            worker.environment['PATH'] = os.path.join(worker.cwd, '.venv', 'bin') + ':' + worker.environment.get('PATH', '')
        worker.environment['VIRTUAL_ENV'] = os.path.join(worker.cwd, '.venv')

    def __str__(self):
        return '<%s script=\'%s\' labels=\'%s\'>' % (type(self).__name__, self.script, self.labels)

    def __repr__(self):
        return self.__str__()


class LocalJob(Job):
    def __init__(self, script, path):
        super(LocalJob, self).__init__(script, {'path': path})

    def setup(self, worker):
        super(LocalJob, self).setup(worker)

        worker.environment['ARTISAN_BUILD_TYPE'] = 'local'


class GitJob(Job):
    def __init__(self, script, repo, branch):
        params = {'repo': repo,
                  'branch': branch}
        super(GitJob, self).__init__(script, params)

    def setup(self, worker):
        super(GitJob, self).setup(worker)

        worker.environment['ARTISAN_BUILD_TYPE'] = 'git'
        worker.environment['ARTISAN_GIT_SLUG'] = self.params['repo']
        worker.environment['ARTISAN_GIT_BRANCH'] = self.params['branch']

        tmp_dir = self.make_temporary_directory(worker)
        worker.execute('git clone --depth=50 %s' % self.params['repo'])
        repository = os.path.join(tmp_dir, worker.list_directory()[0])
        worker.change_directory(repository)
        worker.execute('git fetch origin %s' % self.params['branch'])
        worker.execute('git checkout -qf FETCH_HEAD')
