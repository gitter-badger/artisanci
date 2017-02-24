import os
import six
import yaml
from .env_parser import parse_env
from .label_parser import parse_labels
from ..exceptions import ArtisanException
from ..job import Job

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
    'ArtisanYml'
]


class ArtisanYml(object):
    """ Instance describing a project's ``.artisan.yml`` file. """
    def __init__(self):
        self.jobs = []

    @staticmethod
    def from_path(path):
        """ Loads a :class:`artisan.yml.ProjectYml` instance
        from a path. Can be either a directory (where it will
        search for a proper file) or an actual file.

        :param str path: Directory or file to read ``.artisan.yml`` from.
        :rtype: artisan.yml.ArtisanYml
        :return: :class:`artisan.yml.ArtisanYml` instance.
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
        """ Loads a :class:`artisan.yml.ArtisanYml` instance
        from a string.

        :param str string: String of a ``.artisan.yml`` file.
        :rtype: artisan.yml.ArtisanYml
        :return: :class:`artisan.yml.ArtisanYml` instance.
        """
        jobs = []
        artisan_yml = yaml.load(string)

        if 'jobs' not in artisan_yml:
            raise ArtisanException('Could not parse project configuration. '
                                   'Requires a `jobs` entry.')
        for job_json in artisan_yml['jobs']:
            if 'name' not in job_json:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `name` entry in each job.')
            if 'script' not in job_json:
                raise ArtisanException('Could not parse project configuration. '
                                       'Requires a `script` entry in each job.')

            job = Job(job_json['name'], job_json['script'], {})

            if 'labels' in job_json:
                for label_json in parse_labels(job_json['labels']):
                    job = Job(job_json['name'], job_json['script'], {})
                    for key, value in six.iteritems(label_json):
                        job.labels[key] = value
            if 'env' in job_json:
                job.environment = parse_env(job_json['env'])

            jobs.append(job)

        project = ArtisanYml()
        project.jobs.extend(jobs)
        return project
