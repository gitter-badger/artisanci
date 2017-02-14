import sys
import requests
import colorama
colorama.init()

__all__ = [
    'Report',
    'CommandLineReport'
]


class Report(object):
    def __init__(self):
        self._state = 'install'

    def set_state(self, state):
        self._state = state

    def next_command(self, command):
        raise NotImplementedError()

    def output_command(self, output):
        raise NotImplementedError()


class CommandLineReport(Report):
    def next_command(self, command):
        print(colorama.Fore.YELLOW + '$ ' + command + colorama.Style.RESET_ALL)

    def output_command(self, output, error=False):
        sys.stdout.write((colorama.Fore.LIGHTRED_EX if error else '') + output + colorama.Style.RESET_ALL)
        sys.stdout.flush()
