import re
from .classifier import Classifier

_WINDOWS_VERSION_REGEX = re.compile(r'^\(\'[^\']+\', \'([^\']+)\'')


def detect_platform(worker):
    if worker.platform == 'Windows':
        yield from detect_windows(worker)
    elif worker.platform == 'Mac OS':
        yield from detect_mac(worker)
    else:
        yield from detect_linux_platform(worker)


def detect_windows(worker):
    command = worker.execute('python -c "import sys, platform; sys.stdout'
                             '.write(str(platform.win32_ver()))"')
    if command.wait(timeout=5.0) and command.exit_status == 0:
        stdout = command.stdout.read().decode('utf-8')
        match = _WINDOWS_VERSION_REGEX.match(stdout)
        if match:
            name = 'windows'
            version, = match.groups()
            yield Classifier(name, version)


def detect_mac(worker):
    pass


def detect_linux_platform(worker):
    pass