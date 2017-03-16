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

""" Module for a single description of a build from `.artisan.yml`. """

from ..exceptions import ArtisanException
from ..watchable import Watchable

__all__ = [
    'BuildYml'
]


class BuildYml(Watchable):
    def __init__(self, script, duration):
        super(BuildYml, self).__init__()
        if len(script) > 256:
            raise ArtisanException('`script` cannot be longer than 256 characters.')
        if duration > 2 * 60:
            raise ArtisanException('`duration` cannot be longer than an hour (60 minutes).')
        self.script = script
        self.environment = {}
        self.requires = {}
        self.duration = duration
