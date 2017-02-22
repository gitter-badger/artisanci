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


class Label(object):
    def __init__(self, name, type=None, version=None):
        self.name = name
        self.type = type
        self.version = version

    def __eq__(self, other):
        if isinstance(other, Label):
            return (self.name == other.name and
                    self.type == other.type and
                    self.version == other.version)
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Label):
            return (self.name != other.name or
                    self.type != other.type or
                    self.version != other.version)
        else:
            return NotImplemented

    def __str__(self):
        string = self.name
        if self.type:
            string += ':' + self.type
        if self.version:
            string += '==' + self.version
        return string

    def __repr__(self):
        return self.__str__()
