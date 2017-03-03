import os
import six
import sys
import uuid
from ..exceptions import ArtisanException
from ..report import DoNothingReport
from ..worker import Worker

__all__ = [
    'BaseJob'
]


class BaseJob(object):
    def __init__(self, name, script, params):
        self.name = name
        self.script = script
        self.params = params
        self.report = None
        self.labels = {}
        self.environment = {}

        self._cleanup_calls = []

    def setup(self, worker):
        assert isinstance(worker, Worker)
        worker.add_listener(self.report)

        self.setup_environment(worker)

        if 'python' in self.params:
            self.setup_python(worker)

    def execute(self, worker):
        # Executing each part of the script.
        error = None
        script = None

        # If the Job doesn't have a report attached
        # then we're just going to do nothing.
        if self.report is None:
            self.report = DoNothingReport()

        self.report.on_status_change('setup')
        try:
            self.setup(worker)

            # All environment setup is completed, time to display them.
            self.display_environment(worker)

            script = self.setup_script(worker)
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
            self.report.on_command_error('%s: %s' % (type(error).__name__, str(error)))
        if error is not None:
            try:
                if hasattr(script, 'after_failure'):
                    self.report.on_status_change('after_failure')
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

    def display_environment(self, worker):
        # Show all environment variables sorted.
        self.report.on_next_command('env')
        line_feed = '\r\n' if worker.platform == 'Windows' else '\n'
        for key, value in sorted(worker.environment.items()):
            self.report.on_command_output('%s=%s%s' % (key, value,
                                                       line_feed))

    def setup_script(self, worker):
        script_path = self.script
        if os.path.isabs(script_path):
            script_path = os.path.join(worker.cwd, script_path)
        if not worker.isfile(script_path):
            raise ArtisanException('Could not find the script `%s` '
                                   'within the project.' % script_path)
        script_module = os.path.basename(script_path)
        if script_module.endswith('.py'):
            script_module = script_module[:-3]
        sys.path.insert(0, os.path.dirname(script_path))
        script = __import__(script_module)
        sys.path = sys.path[1:]
        return script

    def setup_environment(self, worker):
        # Filter all external environment variables
        no_filter = {'PATH', 'LD_LIBRARY_PATH', 'SYSTEMPATH'}
        for key in six.iterkeys(worker.environment.copy()):
            if key not in no_filter:
                del worker.environment[key]

        # Setup the environment for the job
        for key, value in six.iteritems(self.environment):
            worker.environment[key] = value

        # Setup all default environment variables
        worker.environment['ARTISAN'] = 'true'
        worker.environment['CI'] = 'true'
        worker.environment['CONTINUOUS_INTEGRATION'] = 'true'
        worker.environment['ARTISAN_BUILD_TRIGGER'] = 'manual'

        # Set the Artisan version.
        from .. import __version__
        worker.environment['ARTISAN_VERSION'] = __version__

        # Set the build directory to the current directory.
        worker.environment['ARTISAN_BUILD_DIR'] = worker.cwd

    def make_temporary_directory(self, worker):
        assert isinstance(worker, Worker)
        worker.chdir(worker.tmp)
        tmp_dir = uuid.uuid4().hex
        while worker.isdir(tmp_dir):
            tmp_dir = uuid.uuid4().hex
        worker.mkdir(tmp_dir)
        worker.chdir(tmp_dir)
        tmp_dir = worker.cwd
        self.add_cleanup(worker.remove, tmp_dir)
        return tmp_dir

    def as_args(self):
        """
        Converts the Job into arguments to be run as if run by
        ``python -m artisan ...[job.as_args()]``
        """
        raise NotImplementedError()

    def setup_python(self, worker):
        venv = os.path.join(worker.tmp, '.artisan-ci-venv')
        if worker.isdir(venv):
            worker.remove(venv)
        worker.execute('virtualenv -p %s %s' % (self.params['python'], venv))
        if worker.platform == 'Windows':
            worker.environment['PATH'] = (os.path.join(venv, 'Scripts') + ';' +
                                          worker.environment.get('PATH', ''))
        else:
            worker.environment['PATH'] = (os.path.join(venv, 'bin') + ':' +
                                          worker.environment.get('PATH', ''))
        worker.environment['VIRTUAL_ENV'] = venv
        self.add_cleanup(worker.remove, venv)

    def __str__(self):
        return '<%s script=\'%s\' labels=\'%s\'>' % (type(self).__name__,
                                                     self.script,
                                                     self.labels)

    def __repr__(self):
        return self.__str__()
