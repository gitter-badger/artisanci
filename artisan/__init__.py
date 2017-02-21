"""
      __        _______  ___________  __      ________     __      _____  ___
     /""\      /"      \("     _   ")|" \    /"       )   /""\    (\"   \|"  \
    /    \    |:        |)__/  \\__/ ||  |  (:   \___/   /    \   |.\\   \    |
   /' /\  \   |_____/   )   \\_ /    |:  |   \___  \    /' /\  \  |: \.   \\  |
  //  __'  \   //      /    |.  |    |.  |    __/  \\  //  __'  \ |.  \    \. |
 /   /  \\  \ |:  __   \    \:  |    /\  |\  /" \   :)/   /  \\  \|    \    \ |
(___/    \___)|__|  \___)    \__|   (__\_|_)(_______/(___/    \___)\___|\____\)

         `Open-Source Continuous Integration Services that work for you!`
                      Copyright (c) 2017 Seth Michael Larson
          ______________________________________________________________

          Licensed under the Apache License, Version 2.0 (the "License");
          you may not use this file except in compliance with the License.
          You may obtain a copy of the License at:

                    http://www.apache.org/licenses/LICENSE-2.0

          Unless required by applicable law or agreed to in writing,
          software distributed under the License is distributed on an
          "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
          either express or implied. See the License for the specific
          language governing permissions and limitations under the License.
          ______________________________________________________________
"""
from .exceptions import (ArtisanException,
                         ArtisanAPIException,
                         CommandTimeoutException,
                         CommandExitStatusException)
from .worker import (Worker,
                     Command)
from .executor import (LocalExecutor,
                       VirtualBoxExecutor)

__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__license__ = 'Apache-2.0'
__version__ = 'dev'

__all__ = [
    'ArtisanException',
    'ArtisanAPIException',
    'CommandTimeoutException',
    'CommandExitStatusException',
    'Worker',
    'Command',
    'LocalExecutor',
    'VirtualBoxExecutor'
]
