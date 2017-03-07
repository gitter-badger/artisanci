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

""" Module for parsing the env expression
from the projects ``.artisan.yml`` file. """

import re
import six
from ..exceptions import ArtisanException

__all__ = [
    'parse_env'
]

_ENVIRONMENT_VARIABLE_REGEX = re.compile(r'^([^=]+)=(.*)$')


def parse_env(env):
    """ Parses an ``env`` expression within a job definition.
    ``env`` can either be a dictionary of values or a list of
    'ENV=VALUE' values. """
    if isinstance(env, dict):
        for key, value in six.iteritems(env):
            # Convert naked YAML constants into proper strings.
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            if isinstance(value, int):
                value = str(value)

            if not isinstance(key, str) or not isinstance(value, str):
                raise ArtisanException('Project configuration `artisan.yml` is not '
                                       'structured properly. See the documentation '
                                       'for more details.')

            env[key] = value
        return env
    elif isinstance(env, list):
        environment = {}
        for entry in env:
            match = _ENVIRONMENT_VARIABLE_REGEX.match(entry)
            if match:
                key, value = match.groups()
                if key in environment:
                    raise ArtisanException('There is a duplicate key `%s` '
                                           'in `env` definition.' % key)
                environment[key] = value
            else:
                raise ArtisanException('Could not parse `env` entry `%s`. Must '
                                       'be of the form `KEY=VALUE`' % entry)
        return environment
    elif isinstance(env, str):
        match = _ENVIRONMENT_VARIABLE_REGEX.match(env)
        if match:
            key, value = match.groups()
            return {key: value}
        else:
            raise ArtisanException('Could not parse `env` entry `%s`. Must '
                                   'be of the form `KEY=VALUE`' % env)
    else:
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly. See the documentation '
                               'for more details.')
