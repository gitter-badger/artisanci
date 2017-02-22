import platform
from ._clean import clean_label

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
    'detect_platform_labels'
]


def detect_platform_labels():
    """ Detects all labels for platforms. """
    try:
        return detect_linux_platform_labels()
    except ImportError:
        return detect_non_linux_platform_labels()


def detect_linux_platform_labels():
    """ Detects Linux distro identification with version. """
    import distro  # distro throws an ImportError if called on a non-Linux platform.
    return [{'platform': (clean_label(distro.id()), distro.version())}]


def detect_non_linux_platform_labels():
    """ Detects non-Linux platform labels. """
    if platform.system() == 'Windows':
        _, version, _, _ = platform.win32_ver()
        return [{'platform': ('windows', version)}]
    elif platform.system() == 'Darwin':
        _, (version, _, _, _), _ = platform.mac_ver()
        return [{'platform': ('osx', version)}]
    else:
        system, _, _, version, _, _ = platform.uname()
        return [{'platform': (clean_label(system), version)}]
