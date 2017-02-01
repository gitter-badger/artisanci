import re
from .classifier import Classifier


_PYTHON_VERSION_REGEX = re.compile(r'^\([a-z._]+\(major=(\d+), minor=(\d+), micro=(\d+)[a-z\d=\' ,]+\)'
                                   r', \'([A-Za-z]+)\', \'([^\']+)\'\)$')


def detect_python(worker):
    """
    Detects all Python installations on the Worker.

    :param artisan.worker.BaseWorker worker: Worker to detect Python on.
    :return: List of classifiers.
    """
    cmd = ('%s -c \"import sys, platform; sys.stdout.write(str('
           '(sys.version_info, platform.python_implementation(),'
           'sys.executable)))\"')
    commands = []
    for suffix in ['', '2', '3']:
        commands.append(worker.execute(cmd % 'python' + suffix))
    for major, minor in [(2, 7), (3, 3), (3, 4), (3, 5), (3, 6)]:
        commands.append(worker.execute(cmd % ('python%d.%d' % (major, minor))))

    for command in commands:
        if command.wait(timeout=5.0) and command.exit_status == 0:
            stdout = command.stdout.read().decode('utf-8')
            match = _PYTHON_VERSION_REGEX.match(stdout)
            if match:
                major, minor, micro, implementation, path = match.groups()
                version = '%s.%s' % (major, minor)
                if implementation == 'CPython':
                    name = 'cpython'
                    classifer = Classifier('python', version)
                    classifer.info['path'] = path
                    yield classifer
                elif implementation == 'IronPython':
                    name = 'iron-python'
                elif implementation == 'Jython':
                    name = 'jython'
                elif implementation == 'PyPy':
                    name = 'pypy'
                else:
                    continue
                classifer = Classifier(name, version)
                classifer.info['path'] = path
                yield classifer
