"""
  __   ____  ____  __  ____   __   __ _     ___  __
 / _\ (  _ \(_  _)(  )/ ___) / _\ (  ( \   / __)(  )
/    \ )   /  )(   )( \___ \/    \/    /  ( (__  )(
\_/\_/(__\_) (__) (__)(____/\_/\_/\_)__)   \___)(__)

    * Community-Powered Continuous Integration! *
       Copyright (c) 2017 Seth Michael Larson
"""

from .exceptions import ArtisanException
from .builds import (BaseBuild,
                     LocalBuild,
                     GitBuild,
                     MercurialBuild)
from .builders import (BaseBuilder,
                       LocalBuilder,
                       VirtualBoxBuilder)
from .workers import (Command,
                      Worker)
from .yml import ArtisanYml

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
__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__license__ = 'Apache-2.0'
__version__ = 'dev'

__all__ = [
    'ArtisanException',
    'ArtisanYml',
    'BaseBuilder',
    'BaseBuild',
    'Command',
    'GitBuild',
    'LocalBuilder',
    'LocalBuild',
    'MercurialBuild',
    'VirtualBoxBuilder',
    'Worker'
]
