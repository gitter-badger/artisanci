""" Command implementation for Python 3.x+ """

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
from .base_command_impl import BaseCommandImpl

__all__ = [
    'Command3'
]


class Command3(BaseCommandImpl):
    def __init__(self, worker, command, environment=None):
        super(Command3, self).__init__(worker, command, environment)

    def _read_all(self, timeout=0.0):
        if self._proc is None:
            return
        self._exit_status = self._proc.poll()
        stdin = None
        if self._stdin.tell():
            self._stdin.seek(0, 0)
            stdin = self._stdin.read()
            self._stdin.truncate(0)
        try:
            stdout, stderr = self._proc.communicate(input=stdin,
                                                    timeout=timeout)

        # Subprocess will raise a ValueError if stdin is
        # attempted to write to but the file is closed.
        except (subprocess.TimeoutExpired, ValueError):
            stdout, stderr = b'', b''
        if self._exit_status is None:
            if self._proc and self._proc.returncode is not None:
                self._exit_status = self._proc.returncode
        if stdout:
            self._write_data_to_stream(self._stdout, stdout)
            stdout = stdout.decode('utf-8')
            self.worker.report.output_command(stdout)
        if stderr:
            self._write_data_to_stream(self._stderr, stderr)
            stderr = stderr.decode('utf-8')
            self.worker.report.output_command(stderr, True)
