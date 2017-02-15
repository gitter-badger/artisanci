import sys
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

    def output_command(self, output, error=False):
        raise NotImplementedError()

    def build_success(self):
        raise NotImplementedError()

    def build_failure(self):
        raise NotImplementedError()


class CommandLineReport(Report):
    def set_state(self, state):
        super(CommandLineReport, self).set_state(state)
        print(colorama.Fore.LIGHTCYAN_EX + state + ':' + colorama.Style.RESET_ALL)

    def next_command(self, command):
        print(colorama.Fore.YELLOW + '$ ' + command + colorama.Style.RESET_ALL)

    def output_command(self, output, error=False):
        sys.stdout.write((colorama.Fore.LIGHTRED_EX if error else '') + output + colorama.Style.RESET_ALL)
        sys.stdout.flush()

    def build_success(self):
        print(colorama.Fore.LIGHTGREEN_EX + 'Done. Your build completed successfully.' + colorama.Style.RESET_ALL)

    def build_failure(self):
        print(colorama.Fore.LIGHTRED_EX + 'Done. Your build completed with errors.' + colorama.Style.RESET_ALL)
