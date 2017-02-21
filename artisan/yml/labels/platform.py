import platform
from ._clean import clean_label

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
    import distro
    return [{'platform': (clean_label(distro.id()), distro.version())}]


def detect_non_linux_platform_labels():
    """ Detects non-Linux platform labels such as Windows, OSX, and Jython. """
    if platform.system() == 'Windows':
        _, version, _, _ = platform.win32_ver()
        return [{'platform': ('windows', version)}]
    elif platform.system() == 'Darwin':
        _, (version, _, _, _), _ = platform.mac_ver()
        return [{'platform': ('osx', version)}]
    elif platform.system() == 'Java':
        _, _, _, (system, version, _) = platform.java_ver()
        return [{'platform': (clean_label(system), version)}]
    else:
        system, _, _, version, _, _ = platform.uname()
        return [{'platform': (clean_label(system), version)}]
