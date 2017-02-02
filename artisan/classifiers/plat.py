import re
from .classifier import Classifier
from .plat_linux import detect_linux_platform

_WINDOWS_VERSION_REGEX = re.compile(r'^\(\'[^\']+\', \'([^\']+)\'')


def detect_platform(worker):
    if worker.platform == 'Windows':
        return detect_windows(worker)
    elif worker.platform == 'Mac OS':
        return
    else:
        for x in detect_linux_platform(worker):
            yield x


def detect_windows(worker):
    command = worker.execute('python -c "import sys, platform; sys.stdout'
                             '.write(str(platform.win32_ver()))"')
    if command.wait(timeout=5.0) and command.exit_status == 0:
        stdout = command.stdout.read().decode('utf-8')
        match = _WINDOWS_VERSION_REGEX.match(stdout)
        if match:
            name = 'windows'
            version, = match.groups()
            return [Classifier(name, version, family='platform')]
    return []


def detect_mac(worker):
    yield Classifier('osx', '?.?')
