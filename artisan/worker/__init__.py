""" Module containing all interfaces and
implementations of the workers used by Artisan. """

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

from .file_attrs import FileAttributes
from .base_worker import BaseWorker
from .local_worker import LocalWorker
from .ssh_worker import SshWorker
from .remote_worker import RemoteWorker
from .command import BaseCommand

__all__ = [
    'BaseWorker',
    'LocalWorker',
    'FileAttributes',
    'SshWorker',
    'RemoteWorker',
    'BaseCommand'
]
