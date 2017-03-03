#           Copyright (c) 2017 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

""" Module for the base Job interface. """

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

    def run(self, worker):
        """ Run the job using a worker. """
        # Executing each part of the script.
        error = None
        script = None

        # If the Job doesn't have a report attached
        # then we're just going to do nothing.
        if self.report is None:
            self.report = DoNothingReport()

        self.report.on_status_change('setup')
        try:
            self.setup_job(worker)

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
            self.cleanup_job(worker)
        except Exception:
            pass
        if error is not None:
            self.report.on_status_change('failure')
        else:
            self.report.on_status_change('success')

    def setup_job(self, worker):
        assert isinstance(worker, Worker)
        worker.add_listener(self.report)

        self.setup_environment(worker)

        if 'python' in self.params:
            self.setup_python(worker)

    def cleanup_job(self, worker):
        for func, args, kwargs in self._cleanup_calls:
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        worker.remove_listener(self.report)

    def add_cleanup(self, func, *args, **kwargs):
        """
        Adds a function to be called during the clean-up phase for the worker.

        :param func: Function to be called.
        :param args: Positional arguments to be passed to the function.
        :param kwargs: Key-word arguments to be passed to the function.
        """
        self._cleanup_calls.append((func, args, kwargs))

    def display_environment(self, worker):
        """ Shows the environment variables the worker is using. """
        # Show all environment variables sorted.
        self.report.on_next_command('env')
        line_feed = '\r\n' if worker.platform == 'Windows' else '\n'
        for key, value in sorted(worker.environment.items()):
            self.report.on_command_output('%s=%s%s' % (key, value,
                                                       line_feed))

    def setup_script(self, worker):
        """ Loads the script into a module. """
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
        """ Sets up the environment for the worker. """
        # Filter all external environment variables
        no_filter = {'PATH', 'LD_LIBRARY_PATH', 'SYSTEMROOT'}
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
        """ Creates and navigates to a temporary directory. """
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

    def setup_python(self, worker):
        """ Creates a Python virtual environment from a Python interpreter. """
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

    def as_args(self):
        """
        Converts the Job into arguments to be run as if run by
        ``python -m artisan ...[job.as_args()]``
        """
        raise NotImplementedError()
