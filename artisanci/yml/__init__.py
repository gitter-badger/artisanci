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
from .job import JobYml
from .label_parser import parse_labels
from .farms_parser import parse_farms
from ..exceptions import ArtisanException

__all__ = [
    'ArtisanYml',
    'JobYml'
]


class ArtisanYml(object):
    """ Instance describing a project's ``.artisan.yml`` file. """
    def __init__(self):
        self.jobs = []
        self.source_farms = []
        self.include_farms = []
        self.omit_farms = []
        self.community_farms = False

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
        :param str path: Optional, if given means that this function was called from_path().
        :rtype: artisan.ArtisanYml
        :return: :class:`artisan.ArtisanYml` instance.
        """
        artisan_yml = yaml.load(string)
        project = ArtisanYml()

        if 'jobs' not in artisan_yml:
            raise ArtisanException('Could not parse project configuration. '
                                   'Requires a `jobs` entry.')
        for job_yml in artisan_yml['jobs']:
            if 'name' not in job_yml:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `name` entry in each job.')
            if 'script' not in job_yml:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `script` entry in each job.')

            env = {}
            if 'env' in job_yml:
                env = parse_env(job_yml['env'])

            if 'labels' in job_yml:
                for label_json in parse_labels(job_yml['labels']):
                    job = JobYml(name=job_yml['name'],
                                 script=job_yml['script'])
                    for key, value in six.iteritems(label_json):
                        job.labels[key] = value
                    job.environment = env
                    project.jobs.append(job)
            else:
                job = JobYml(name=job_yml['name'],
                             script=job_yml['script'])
                job.environment = env
                project.jobs.append(job)

        if 'farms' in artisan_yml:
            sources, include, omit, community = parse_farms(artisan_yml['farms'])
            project.source_farms = sources
            project.include_farms = include
            project.omit_farms = omit
            project.community_farms = community
        else:
            project.community_farms = True
            project.source_farms = ['https://farms.artisan.io']

        return project
