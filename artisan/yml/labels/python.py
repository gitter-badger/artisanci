import re
import subprocess

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

_PYTHON_VERSION_REGEX = re.compile('Python ([0-9.]+)')
_PIP_VERSION_REGEX = re.compile('pip ([0-9.]+)')

__all__ = [
    'detect_python_labels'
]


def detect_python_labels():
    """ Detects Python and Python packages. """
    labels = []

    # Detecting `Python` versions.
    for version in ['', '2.6', '2.7', '3.3', '3.4', '3.5', '3.6', '3.7']:
        try:
            popen = subprocess.Popen('python%s --version' % version,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout, stderr = popen.communicate(timeout=1.0)
            if not isinstance(stdout, str):
                stdout = stdout.decode('utf-8')
                stderr = stderr.decode('utf-8')
            match = _PYTHON_VERSION_REGEX.search(stdout)
            if match is not None:
                version = match.group(1)
                labels.append({'python': ('cpython', version)})
            else:
                match = _PYTHON_VERSION_REGEX.search(stderr)
                if match is not None:
                    version = match.group(1)
                    labels.append({'python': ('cpython', version)})
        except Exception:
            pass

    # Detecting `pip` version
    try:
        popen = subprocess.Popen('python -m pip --version',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        output, _ = popen.communicate(timeout=1.0)
        assert popen.returncode is not None
        if not isinstance(output, str):
            output = output.decode('utf-8')
        match = _PIP_VERSION_REGEX.search(output)
        if match is not None:
            version = match.group(1)
            labels.append({'python-pip': (None, version)})
    except Exception:
        pass
    else:
        # Detecting `setuptools` version
        try:
            popen = subprocess.Popen('python -c "import setuptools; print(setuptools.__version__)',
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            output, _ = popen.communicate(timeout=1.0)
            assert popen.returncode is not None
            if not isinstance(output, str):
                output = output.decode('utf-8')
            labels.append({'python-setuptools': (None, output.strip())})
        except Exception:
            pass

    # Detecting `virtualenv` version.
    try:
        popen = subprocess.Popen('python -m virtualenv --version',
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        output, _ = popen.communicate(timeout=1.0)
        assert popen.returncode is not None
        if not isinstance(output, str):
            output = output.decode('utf-8')
        labels.append({'python-virtualenv': (None, output.strip())})
    except Exception:
        pass

    return labels
