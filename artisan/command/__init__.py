from .base import BaseCommand
import sys

if sys.version_info >= (3, 0, 0):
    from .local3 import Local3Command as LocalCommand
else:
    from .local2 import Local2Command as LocalCommand

__all__ = [
    'BaseCommand',
    'LocalCommand'
]
