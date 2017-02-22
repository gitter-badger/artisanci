from .platform import detect_platform_labels
from .python import detect_python_labels
from .machine import detect_machine_labels
from .label import Label

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
    'detect_labels'
]


def detect_labels():
    detects = []
    detects.extend(detect_platform_labels())
    detects.extend(detect_python_labels())
    detects.extend(detect_machine_labels())
    labels = []
    for kw in detects:
        for name, (type, version) in kw.items():
            labels.append(Label(name, type, version))
    return labels
