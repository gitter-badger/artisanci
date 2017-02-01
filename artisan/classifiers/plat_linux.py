""" Classifier detector for Linux platform and distro. """
import re
import posixpath
from .classifier import Classifier
from ..worker import BaseWorker
from ..vendor.distro import (LinuxDistribution,
                             _DISTRO_RELEASE_BASENAME_PATTERN,
                             _DISTRO_RELEASE_IGNORE_BASENAMES)

_UNAME_RELEASE_REGEX = re.compile(r'^(\d+)\.(\d+)(?:\.(\d+))?')


def detect_linux_platform(worker):
    classifiers = []

    dist = WorkerLinuxDistribution(worker)
    major, minor, micro = dist.version_parts(best=True)
    if micro == '':
        version = '%s.%s' % (major, minor)
    else:
        version = '%s.%s.%s' % (major, minor, micro)
    name = dist.id()
    classifiers.append(Classifier(name, version, family='platform'))
    if dist.codename().lower() != name:
        classifiers.append(Classifier(dist.codename().lower(), version, family='platform'))
    classifiers.extend(detect_linux_kernel(worker))
    return classifiers


def detect_linux_kernel(worker):
    try:
        with worker.execute('uname -r') as c:
            if c.wait(timeout=5.0) and c.exit_status == 0:
                stdout = c.stdout.read().decode('utf-8')
                match = _UNAME_RELEASE_REGEX.match(stdout)
                if match:
                    major, minor, micro = match.groups()
                    if micro == '':
                        version = '%s.%s' % (major, minor)
                    else:
                        version = '%s.%s.%s' % (major, minor, micro)
                    return [Classifier('linux', version)]
    except Exception:
        return []


class WorkerLinuxDistribution(LinuxDistribution):
    """ Implementation of distro.LinuxDistribution which
    reads information from a artisan.worker.BaseWorker instead. """
    def __init__(self, worker):
        assert isinstance(worker, BaseWorker)
        self._worker = worker
        self._unix_conf_dir = self._worker.environment.get('UNIXCONFDIR', '/etc')
        super(WorkerLinuxDistribution, self).__init__()

    def _get_os_release_info(self):
        try:
            with self._worker.open_file(self.os_release_file) as f:
                return self._parse_os_release_content(f)
        except (IOError, OSError):
            return {}

    def _get_lsb_release_info(self):
        cmd = 'lsb_release -a'
        try:
            with self._worker.execute(cmd) as c:
                if c.wait(timeout=5.0) and c.exit_status == 0:
                    stdout = c.stdout.read().decode('utf-8')
                    return self._parse_lsb_release_content(stdout.split('\n'))
                return {}
        except Exception:
            return {}

    def _get_distro_release_info(self):
        if self.distro_release_file:
            self._parse_distro_release_file(self.distro_release_file)
        else:
            basenames = self._worker.list_directory(self._unix_conf_dir)
            basenames.sort()
            for basename in basenames:
                if basename in _DISTRO_RELEASE_IGNORE_BASENAMES:
                    continue
                match = _DISTRO_RELEASE_BASENAME_PATTERN.match(basename)
                if match:
                    path = posixpath.join(self._unix_conf_dir, basename)
                    distro_info = self._parse_distro_release_file(path)
                    distro_info['id'] = match.group(1)
                    return distro_info
        return {}

    def _parse_distro_release_file(self, path):
        try:
            with self._worker.open_file(path) as f:
                distro_info = self._parse_distro_release_content(f.readline())
        except (IOError, OSError):
            distro_info = {}

        basename = posixpath.basename(self.distro_release_file)
        match = _DISTRO_RELEASE_BASENAME_PATTERN.match(basename)
        if match:
            distro_info['id'] = match.group(1)

        return distro_info
