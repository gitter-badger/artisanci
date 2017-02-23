import os
import six
import yaml
from .parser import expand_labels
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


class ProjectYml(object):
    def __init__(self):
        self.jobs = []


def parse_project_yaml(path):
    """
    Parses a ``.artisan.yml`` file into a list of :class:`artisan.Job` instances
    that are ready to be executed or sent to the farms.

    :param str path: Either the path to a ``.artisan.yml`` file or the project root.
    :return: List of :class:`artisan.Job` instances.
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

    jobs = []
    with open(yml, 'r') as f:
        artisan_yml = yaml.load(f.read())

        if 'jobs' not in artisan_yml:
            raise ArtisanException('Could not parse project configuration. Requires a `job` entry.')
        for job_json in artisan_yml['jobs']:
            if 'name' not in job_json:
                raise ArtisanException('Could not parse project configuration. Requires a `name` entry in each job.')
            if 'script' not in job_json:
                raise ArtisanException('Could not parse project configuration. Requires a `script` entry in each job.')
            if 'labels' in job_json:
                for label_json in expand_labels(job_json['labels']):
                    job = Job(job_json['script'], {})
                    for key, value in six.iteritems(label_json):
                        job.labels[key] = value
                    jobs.append(job)
            else:
                jobs.append(Job(job_json['script'], {}))

    project = ProjectYml()
    project.jobs.extend(jobs)
    return project
