import sys
from .base_command import BaseCommand
from .ssh_command import SshCommand
from .remote_command import RemoteCommand

if sys.version_info >= (3, 0, 0):
    from .local_command3 import LocalCommand3 as LocalCommand
else:
    from .local_command2 import LocalCommand2 as LocalCommand

__all__ = [
    'BaseCommand',
    'LocalCommand',
    'SshCommand',
    'RemoteCommand'
]
