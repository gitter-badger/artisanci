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

__all__ = [
    'BaseJob'
]


class BaseJob(object):
    def __init__(self, name, script):
        self.name = name
        self.script = script
        self.report = None
        self.labels = {}
        self.environment = {}

    def execute_project(self, worker):
        worker.environment['ARTISAN_BUILD_DIR'] = worker.cwd

        self.display_worker_environment(worker)
        script = self.load_script(worker)

        try:
            if hasattr(script, 'install'):
                sys.stdout.write('I')
                sys.stdout.flush()
                script.install(worker)

            if hasattr(script, 'script'):
                sys.stdout.write('S')
                sys.stdout.flush()
                script.script(worker)

            sys.stdout.write('P')
            if hasattr(script, 'after_success'):
                sys.stdout.flush()
                script.after_success(worker)

        except Exception as e:
            sys.stdout.write('F')
            if hasattr(script, 'after_failure'):
                sys.stdout.flush()
                script.after_failure(worker)

    def display_worker_environment(self, worker):
        for name, value in six.iteritems(worker.environment):
            pass

    def load_script(self, worker):
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

    def setup_python_virtualenv(self, worker):
        venv = os.path.join(worker.tmp, uuid.uuid4().hex)
        while worker.isdir(venv):
            venv = os.path.join(worker.tmp, uuid.uuid4().hex)
        worker.execute('virtualenv -p python3.5 %s' % venv)
        if worker.platform == 'Windows':
            worker.environment['PATH'] = (os.path.join(venv, 'Scripts') + ';' +
                                          worker.environment.get('PATH', ''))
        else:
            worker.environment['PATH'] = (os.path.join(venv, 'bin') + ':' +
                                          worker.environment.get('PATH', ''))
        worker.environment['VIRTUAL_ENV'] = venv

    def setup_project(self, worker):
        sys.stdout.write('s'); sys.stdout.flush()
        no_filter = {'PATH', 'LD_LIBRARY_PATH', 'SYSTEMROOT'}
        for key in six.iterkeys(worker.environment.copy()):
            if key not in no_filter and not key.startswith('ARTISAN_'):
                del worker.environment[key]

        from .. import __version__
        worker.environment['ARTISAN_VERSION'] = __version__

        self.setup_python_virtualenv(worker)

    def fetch_project(self, worker):
        pass

    def cleanup_project(self, worker):
        pass

    def as_args(self):
        """
        Converts the Job into arguments to be run as if run by
        ``python -m artisan ...[job.as_args()]``
        """
        raise NotImplementedError()

    def __str__(self):
        return '<%s name=\'%s\' script=\'%s\' labels=%s>' % (type(self).__name__,
                                                             self.name,
                                                             self.script,
                                                             self.labels)

    def __repr__(self):
        return self.__str__()
