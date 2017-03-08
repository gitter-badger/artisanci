import sys
import colorama
colorama.init()


class BaseReporter(object):
    def on_command(self, _, command):
        raise NotImplementedError()

    def on_command_output(self, _, output):
        raise NotImplementedError()


class BasicCommandLineReporter(BaseReporter):
    def on_command(self, _, command):
        print(colorama.Fore.LIGHTYELLOW_EX + '$ ' + command + colorama.Style.RESET_ALL)

    def on_command_output(self, _, output):
        if isinstance(output, bytes):
            output = output.decode('utf-8')
        sys.stdout.write(output)
        sys.stdout.flush()

    def on_status_change(self, _, status):
        if status == 'success':
            print(colorama.Fore.LIGHTGREEN_EX + 'Build Status: SUCCESS' + colorama.Style.RESET_ALL)
        elif status == 'failure':
            print(colorama.Fore.LIGHTGREEN_EX + 'Build Status: FAILURE' + colorama.Style.RESET_ALL)
