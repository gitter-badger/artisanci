import sys
import colorama
from .conf import (update_artisan_toml,
                   parse_artisan_toml,
                   lock_artisan_toml,
                   unlock_artisan_toml)

__all__ = [
    'cli',
    'execute_as_command_line',
    'parse_artisan_toml',
    'update_artisan_toml',
    'lock_artisan_toml',
    'unlock_artisan_toml'
]


def cli():
    """ Command line interface entry point. """
    execute_as_command_line(sys.argv[1:])


def execute_as_command_line(argv):
    colorama.init()
    path = None
    locked = lock_artisan_toml(path)
    if not locked:
        sys.exit(1)
    conf = parse_artisan_toml(path)
