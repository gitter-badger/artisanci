import sys
import colorama
import requests
from .exceptions import ArtisanAPIException
colorama.init()

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
    'Report',
    'CommandLineReport',
    'DoNothingReport'
]


class Report(object):
    def __init__(self):
        self._status = 'waiting'

    def on_next_command(self, command):
        raise NotImplementedError()

    def on_command_output(self, output):
        raise NotImplementedError()

    def on_command_error(self, output):
        raise NotImplementedError()

    def on_status_change(self, status):
        self._status = status

    @property
    def status(self):
        return self._status


class DoNothingReport(Report):
    def on_command_error(self, output):
        pass

    def on_command_output(self, output):
        pass

    def on_next_command(self, command):
        pass


class CommandLineReport(Report):
    def __init__(self):
        super(CommandLineReport, self).__init__()
        self._last_newline = True

    def on_status_change(self, status):
        super(CommandLineReport, self).on_status_change(status)
        if status in ['failure', 'success']:
            if status == 'failure':
                print(('' if self._last_newline else '\r\n') +
                      colorama.Fore.LIGHTRED_EX +
                      'Done. Your build completed with errors.' +
                      colorama.Style.RESET_ALL)
            else:
                print(('' if self._last_newline else '\r\n') +
                      colorama.Fore.LIGHTGREEN_EX +
                      'Done. Your build completed successfully.' +
                      colorama.Style.RESET_ALL)
        else:
            print(('' if self._last_newline else '\r\n') +
                  colorama.Fore.LIGHTCYAN_EX +
                  ' ----- ' + status + ' ----- ' +
                  colorama.Style.RESET_ALL)
        self._last_newline = True

    def on_next_command(self, command):
        print(('' if self._last_newline else '\r\n') +
              colorama.Fore.LIGHTYELLOW_EX +
              '$ ' + command +
              colorama.Style.RESET_ALL)
        self._last_newline = True

    def on_command_output(self, output):
        self._last_newline = '\n' == output[-1]
        sys.stdout.write(output)
        sys.stdout.flush()

    def on_command_error(self, output):
        self._last_newline = '\n' == output[-1]
        sys.stdout.write(colorama.Fore.LIGHTRED_EX +
                         output +
                         colorama.Style.RESET_ALL)
        sys.stdout.flush()


class APIReport(Report):
    def __init__(self, job_id):
        super(APIReport, self).__init__()
        self._job_id = job_id

    def on_status_change(self, status):
        super(APIReport, self).on_status_change(status)
        self._post_api_payload('status_change', status)

    def on_next_command(self, command):
        self._post_api_payload('next_command', command)

    def on_command_output(self, output):
        self._post_api_payload('command_output', output)

    def on_command_error(self, output):
        self._post_api_payload('command_error', output)

    def _post_api_payload(self, event, data):
        payload = {'event': event,
                   'data': data}
        r = requests.post('https://artisan.io/api/job/%s/report' % self._job_id, json=payload)
        if not r.ok:
            raise ArtisanAPIException('API responded with a bad status code: %d' % r.status_code)
