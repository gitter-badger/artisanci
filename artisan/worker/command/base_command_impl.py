""" Partial shared implementation of a BaseCommand. """

#           Copyright (c) 2017 Seth Michael Larson
# _________________________________________________________________
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

import subprocess
from .base_command import BaseCommand

__all__ = [
    'BaseCommandImpl'
]


class BaseCommandImpl(BaseCommand):
    def __init__(self, worker, command, environment=None):
        super(BaseCommandImpl, self).__init__(worker, command, environment)
        self._proc = self._create_subprocess()

    @property
    def pid(self):
        if self._proc is None:
            return None
        return self._proc.pid

    def signal(self, signal):
        if self._proc is not None:
            self._proc.send_signal(signal)
        else:
            raise ValueError('Command is already cancelled.')

    def cancel(self):
        if self._cancelled:
            raise ValueError('Command is already cancelled.')
        try:
            self._proc.kill()
        except Exception:  # Skip coverage.
            pass
        self._proc = None
        self._cancelled = True

    def _create_subprocess(self):
        self._is_shell = True if not isinstance(self.command, list) else False
        return subprocess.Popen(self.command,
                                shell=self._is_shell,
                                cwd=self.worker.cwd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.environment)
