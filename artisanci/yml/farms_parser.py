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

""" Module for parsing the farms expression
from the projects ``.artisan.yml`` file. """

import six
from ..exceptions import ArtisanException

__all__ = [
    'parse_farms'
]


def parse_farms(farms):
    """ Parses the ``farms`` expression in ``artisan.yml`` to show
    where a project is allowed to be executed. """
    if not isinstance(farms, (str, list)):
        raise ArtisanException('Project configuration `artisan.yml` is not '
                               'structured properly at `farms`. See the doc'
                               'umentation for more details.')

    if isinstance(farms, str):
        farms = [farms]

    if len(farms) == 0:
        farms = ['https://farms.artisan.ci']

    return farms
