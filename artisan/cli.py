import argparse
import sys
from .logging import log_error


def main():
    """ Entry point for the Artisan command line utility. """
    execute_as_command_line(sys.argv[1:])


def execute_as_command_line(argv):
    """ Executes Artisan as a command line with the given
    arguments. Typically takes sys.argv but can also be
    used programmatically.

    :param list argv: Arguments as a list of strings.
    """
    if len(argv) == 0:
        log_error('No command given. Must be one of ')