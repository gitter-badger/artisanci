from collections import OrderedDict

import click
import colorama


def prompt_string(question, default):
    return click.prompt(_yellow(question),
                        default=default)


def prompt_password(question):
    return click.prompt(_yellow(question),
                        hide_input=True,
                        default='')


def prompt_yes_or_no(question, default):
    if default:
        default = 'Y/n'
    else:
        default = 'y/N'
    answer = click.prompt(_yellow(question),
                          default=default,
                          type=click.BOOL)
    if isinstance(answer, bool):
        return answer
    if answer == 'Y/n' or answer.lower() in ['y', 'ye', 'yes']:
        return True
    else:
        return False


def prompt_choice(value_name, choices):
    choice_map = OrderedDict((u'%s' % i, value) for i, value in enumerate(choices, 1))
    choice_keys = choice_map.keys()
    choice_lines = [u'%s - %s' % (k, v) for k, v in choice_map.items()]
    prompt = u'\n'.join([u'Select %s:' % value_name,
                         u'\n'.join(choice_lines),
                         u'Choose from %s' % u', '.join(choice_keys)])
    user_choice = click.prompt(_yellow(prompt),
                               type=click.Choice(choice_keys),
                               default=u'1')
    return choice_map[user_choice]


def _yellow(text):
    return colorama.Fore.LIGHTYELLOW_EX + text + colorama.Style.RESET_ALL
