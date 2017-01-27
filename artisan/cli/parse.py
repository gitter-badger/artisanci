import argparse

from .conf import show_artisan_toml
from .prompt import prompt_choice


def parse_domain_conf(argv):
    """
    Parse arguments for the domain `conf`.

    :param list argv: Argv minus the `conf` domain.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--safe', action='store_true')
    parser.add_argument('--path', nargs='?', default=None)

    args = vars(parser.parse_args(argv))
    if args['show']:
        show_artisan_toml(args['path'], args['safe'])


def parse_domain_worker(argv):
    """
    Parse arguments for the domain `conf`.

    :param list argv: Argv minus the `conf` domain.
    """
    print(prompt_choice('What type of worker would you like to add?', ['Local Worker',
                                                                 'SSH Worker',
                                                                 'Remote Worker']))
