import sys
from .base_command import BaseCommand
from .ssh_command import SshCommand

if sys.version_info >= (3, 0, 0):
    from .local_command3 import Local3Command as LocalCommand
else:
    from .local_command2 import Local2Command as LocalCommand

__all__ = [
    'BaseCommand',
    'LocalCommand',
    'SshCommand'
]
