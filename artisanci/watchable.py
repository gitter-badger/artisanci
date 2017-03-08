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

__all__ = [
    'Watchable'
]


class Watchable(object):
    """ Base class for an object that can be watched for events. """
    def __init__(self):
        self._watchers = []

    @property
    def watchers(self):
        return self._watchers

    def add_watcher(self, watcher):
        if watcher in self._watchers:
            raise ValueError('`%s` is already watching `%s`.' % (watcher, self))
        self._watchers.append(watcher)

    def remove_watcher(self, watcher):
        if watcher not in self._watchers:
            raise ValueError('`%s` is not watching `%s`.' % (watcher, self))
        self._watchers.remove(watcher)

    def notify_watchers(self, event_type, data):
        event_handler = 'on_' + event_type
        for watcher in self._watchers:
            if hasattr(watcher, event_handler):
                getattr(watcher, event_handler)(self, data)
