""" All exceptions that are used within Artisan
are defined in this module. """

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

__all__ = [
    'ArtisanException',
    'CommandExitStatusException',
    'CommandTimeoutException'
]


class ArtisanException(Exception):
    pass


class CommandTimeoutException(ArtisanException):
    """ Exception for calling :meth:`artisan.BaseCommand.wait` with
    ``error_on_timeout`` parameter equal to True and the command times out. """
    def __init__(self, command='', timeout=0.0):
        super(CommandTimeoutException, self).__init__(
            'Command `%s` did not exit' % command, timeout)


class CommandExitStatusException(ArtisanException):
    """ Exception for calling :meth:`artisan.BaseCommand.wait` with
    ``error_on_exit`` equal to True and the command exits with
    a non-zero exit status."""
    def __init__(self, command='', exit_status=0):
        super(CommandExitStatusException, self).__init__(
            'Command `%s` exited with a non-zero exit status `%d`' % (command,
                                                                      exit_status))
        self.exit_status = exit_status
