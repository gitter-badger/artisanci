import sys
import colorama
from .conf import (update_artisan_toml,
                   parse_artisan_toml,
                   lock_artisan_toml,
                   unlock_artisan_toml)
from .parse import (parse_domain_conf,
                    parse_domain_worker)

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

    # Swap stdout and stderr so that click prints to stderr.
    tmp = sys.stdout
    sys.stdout = sys.stderr
    sys.stderr = tmp

    try:
        if argv[0] == 'conf':
            parse_domain_conf(argv[1:])
        elif argv[0] == 'worker':
            parse_domain_worker(argv[1:])
    except Exception:
        print(colorama.Fore.RED + 'Ran into an unexpected exception. In order '
              'to help with this issue please post this traceback and the result '
              'of `artisan conf --show --safe` to a new issue in our issue tracker '
              'on Github: `https://github.com/SethMichaelLarson/artisan/issues`.' +
              colorama.Style.RESET_ALL)
        raise
