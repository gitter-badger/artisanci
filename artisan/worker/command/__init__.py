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

import sys
from .base_command import BaseCommand
from .ssh_command import SshCommand
from .remote_command import RemoteCommand

if sys.version_info >= (3, 0, 0):
    from .local_command3 import LocalCommand3 as LocalCommand
else:
    from .local_command2 import LocalCommand2 as LocalCommand

__all__ = [
    'BaseCommand',
    'LocalCommand',
    'SshCommand',
    'RemoteCommand'
]
