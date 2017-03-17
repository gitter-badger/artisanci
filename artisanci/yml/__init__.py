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

import os
import six
import yaml
from .env_parser import parse_env
from .build_yml import BuildYml
from .requires_parser import parse_requires
from ..exceptions import ArtisanException

__all__ = [
    'ArtisanYml',
    'BuildYml'
]


class ArtisanYml(object):
    """ Instance describing a project's ``.artisan.yml`` file. """
    def __init__(self):
        self.jobs = []

    @staticmethod
    def from_path(path):
        """ Loads a :class:`artisan.ArtisanYml` instance
        from a path. Can be either a directory (where it will
        search for a proper file) or an actual file.

        :param str path: Directory or file to read ``.artisan.yml`` from.
        :rtype: artisan.ArtisanYml
        :return: :class:`artisan.ArtisanYml` instance.
        """
        yml = None
        if os.path.isfile(path):
            yml = path
        elif os.path.isdir(path):
            listdir = os.listdir(path)
            if '.artisan.yml' in listdir:
                yml = os.path.join(path, '.artisan.yml')
            elif 'artisan.yml' in listdir:
                yml = os.path.join(path, 'artisan.yml')
        if yml is None:
            raise ArtisanException('Could not find an `.artisan.yml` file in the project root.')
        with open(yml, 'r') as f:
            return ArtisanYml.from_string(f.read())

    @staticmethod
    def from_string(string):
        """ Loads a :class:`artisan.ArtisanYml` instance
        from a string.

        :param str string: String of a ``.artisan.yml`` file.
        :rtype: artisan.ArtisanYml
        :return: :class:`artisan.ArtisanYml` instance.
        """
        artisan_yml = yaml.load(string)
        if not isinstance(artisan_yml, dict):
            raise ArtisanException('Could not parse project configuration. '
                                   'See documentation for more details.')
        project = ArtisanYml()

        if 'builds' not in artisan_yml:
            raise ArtisanException('Could not parse project configuration. '
                                   'Requires a `builds` entry.')
        if not isinstance(artisan_yml['builds'], list):
            raise ArtisanException('Could not parse project configuration. '
                                   '`builds` must be a list type.')
        if len(artisan_yml['builds']) == 0:
            raise ArtisanException('Requires more than one build to run.')
        for build_yml in artisan_yml['builds']:
            if 'script' not in build_yml:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `script` entry in each build.')
            if not isinstance(build_yml['script'], six.string_types):
                raise ArtisanException('The `duration` entry must be either an `str` value.')

            if 'duration' not in build_yml:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `duration` entry in each build.')
            if not isinstance(build_yml['duration'], (float, int)):
                raise ArtisanException('The `duration` entry must be either an '
                                       '`int` or `float` value.')

            env = {}
            if 'env' in build_yml:
                env = parse_env(build_yml['env'])

            if 'requires' in build_yml:
                for label_json in parse_requires(build_yml['requires']):
                    build = BuildYml(script=build_yml['script'],
                                     duration=build_yml['duration'])
                    for key, value in six.iteritems(label_json):
                        build.requires[key] = value
                    build.environment = env
                    project.jobs.append(build)
            else:
                build = BuildYml(script=build_yml['script'],
                                 duration=build_yml['duration'])
                build.environment = env
                project.jobs.append(build)

        return project
