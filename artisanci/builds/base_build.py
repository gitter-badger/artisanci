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

""" Module for the base Build interface. """

import os
import six
import sys
import uuid
from ..exceptions import ArtisanException
from ..yml import BuildYml

__all__ = [
    'BaseBuild'
]


class BaseBuild(BuildYml):
    def __init__(self, build_type, script, duration):
        super(BaseBuild, self).__init__(script, duration)
        self.build_type = build_type
        self.build_id = None
        self.working_dir = None

    @classmethod
    def from_yml(cls, yml, **kwargs):
        if not isinstance(yml, BuildYml):
            raise TypeError('`yml` must be of type `BuildYml`.')
        if cls is BaseBuild:
            raise ValueError('Do not execute BaseBuild.from_yml().')
        return cls(yml.script, yml.duration, **kwargs)

    def fetch_project(self, worker):
        for key, value in six.iteritems(self.environment):
            worker.environment[key] = value

        self.notify_watchers('status_change', 'fetch')

        if self.build_id is None:
            build_id = uuid.uuid4().hex
            while os.path.isdir(os.path.join(worker.tmp, build_id)):
                build_id = uuid.uuid4().hex
            tmp_dir = os.path.join(worker.tmp, build_id)
            self.build_id = build_id
        else:
            tmp_dir = os.path.join(worker.tmp, self.build_id)
        if not worker.isdir(tmp_dir):
            worker.mkdir(tmp_dir)

        self.working_dir = tmp_dir
        worker.chdir(tmp_dir)

    def execute_project(self, worker):
        worker.environment['ARTISAN_BUILD_DIR'] = worker.cwd

        self.display_worker_environment(worker)
        script = self.load_script(worker)

        try:
            if hasattr(script, 'install'):
                self.notify_watchers('status_change', 'install')
                script.install(worker)

            if hasattr(script, 'script'):
                self.notify_watchers('status_change', 'script')
                script.script(worker)

            if hasattr(script, 'after_success'):
                script.after_success(worker)
            self.notify_watchers('status_change', 'success')
        except Exception:
            if hasattr(script, 'after_failure'):
                script.after_failure(worker)
            self.notify_watchers('status_change', 'failure')

    def setup_project(self, worker):
        self.notify_watchers('status_change', 'setup')

        no_filter = {'PATH', 'LD_LIBRARY_PATH', 'SYSTEMROOT'}
        for key in six.iterkeys(worker.environment.copy()):
            if (key not in no_filter and
                    not key.startswith('ARTISAN_') and
                    key not in self.environment):
                del worker.environment[key]

        from .. import __version__
        worker.environment['ARTISAN_VERSION'] = __version__

        self.setup_python_virtualenv(worker)

    def cleanup_project(self, worker):
        self.notify_watchers('status_change', 'cleanup')

        if self.working_dir is not None:
            worker.remove(self.working_dir)

    def display_worker_environment(self, worker):
        self.notify_watchers('command', 'env')
        line_feed = '\r\n' if worker.platform == 'Windows' else '\n'
        for name, value in six.iteritems(worker.environment):
            self.notify_watchers('command_output', '%s=%s%s' % (name, value, line_feed))

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
        worker.execute('virtualenv -p %s %s' % (sys.executable, venv))
        if worker.platform == 'Windows':
            worker.environment['PATH'] = (os.path.join(venv, 'Scripts') + ';' +
                                          worker.environment.get('PATH', ''))
        else:
            worker.environment['PATH'] = (os.path.join(venv, 'bin') + ':' +
                                          worker.environment.get('PATH', ''))
        worker.environment['VIRTUAL_ENV'] = venv

    def as_args(self):
        """
        Converts the Job into arguments to be run as if run by
        ``python -m artisan ...[job.as_args()]``
        """
        raise NotImplementedError()

    def __str__(self):
        return '<%s script=\'%s\' labels=%s>' % (type(self).__name__,
                                                 self.script,
                                                 self.requires)

    def __repr__(self):
        return self.__str__()
