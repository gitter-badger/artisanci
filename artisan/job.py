""" Types of Jobs that can be executed. """
import os
import six
import sys
import uuid
from .exceptions import ArtisanException
from .report import DoNothingReport
from .worker import Worker

__copyright__ = """
          Copyright (c) 2017 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""

__all__ = [
    'BaseJob',
    'LocalJob',
    'GitJob',
    'MercurialJob'
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
        from . import __version__
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


class LocalJob(BaseJob):
    def __init__(self, name, script, path):
        super(LocalJob, self).__init__(name, script, {'path': path})

    def setup(self, worker):
        super(LocalJob, self).setup(worker)
        worker.chdir(self.params['path'])
        worker.environment['ARTISAN_BUILD_TYPE'] = 'local'

    def as_args(self):
        return ['--type', 'local',
                '--script', self.script,
                '--name', self.name,
                '--path', self.params['path']]


class GitJob(BaseJob):
    def __init__(self, name, script, repo, branch, commit=None):
        if commit is None:
            commit = 'HEAD'  # Get the latest if commit is None.

        params = {'repo': repo,
                  'branch': branch,
                  'commit': commit}
        super(GitJob, self).__init__(name, script, params)

    def setup(self, worker):
        super(GitJob, self).setup(worker)

        worker.execute('git --version')

        tmp_dir = self.make_temporary_directory(worker)
        project_root = os.path.join(tmp_dir, 'git-project')
        worker.execute('git clone --depth=50 --branch=%s %s %s' % (self.params['branch'],
                                                                   self.params['repo'],
                                                                   project_root))
        worker.chdir(project_root)
        worker.execute('git checkout -qf %s' % self.params['commit'])

        if self.params['commit'] == 'HEAD':
            rev_parse = worker.execute('git rev-parse HEAD')
            self.params['commit'] = rev_parse.stdout.decode('utf-8').strip()

        self.params['path'] = project_root

        worker.environment['ARTISAN_BUILD_TYPE'] = 'git'
        worker.environment['ARTISAN_GIT_REPOSITORY'] = self.params['repo']
        worker.environment['ARTISAN_GIT_BRANCH'] = self.params['branch']
        worker.environment['ARTISAN_GIT_COMMIT'] = self.params['commit']

    def as_args(self):
        return ['--type', 'git',
                '--script', self.script,
                '--name', self.name,
                '--repo', self.params['repo'],
                '--branch', self.params['branch'],
                '--commit', self.params['commit']]


class MercurialJob(BaseJob):
    def __init__(self, name, script, repo, branch, commit):
        params = {'repo': repo,
                  'branch': branch,
                  'commit': commit}
        super(MercurialJob, self).__init__(name, script, params)

    def setup(self, worker):
        super(MercurialJob, self).setup(worker)

        worker.environment['ARTISAN_BUILD_TYPE'] = 'mercurial'
        worker.environment['ARTISAN_MERCURIAL_REPOSITORY'] = self.params['repo']
        worker.environment['ARTISAN_MERCURIAL_BRANCH'] = self.params['branch']
        worker.environment['ARTISAN_MERCURIAL_COMMIT'] = self.params['commit']

        tmp_dir = self.make_temporary_directory(worker)
        worker.execute('hg clone %s -r %s' % (self.params['repo'], self.params['branch']))
        repository = os.path.join(tmp_dir, worker.list_directory()[0])
        worker.change_directory(repository)

    def as_args(self):
        return ['--type', 'mercurial',
                '--script', self.script,
                '--name', self.name,
                '--repo', self.params['repo'],
                '--branch', self.params['branch']]
