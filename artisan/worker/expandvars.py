""" This file is almost 100% from Python 3.6's implementation
of os.path.expandvars from both `posixpath.py` and `ntpath.py`
with a few minimal changes.

Source: https://hg.python.org/cpython/file/3.6/Lib/ntpath.py
        https://hg.python.org/cpython/file/3.6/Lib/posixpath.py
"""
import re
import string

__all__ = [
    'expandvars'
]
_VARS_POSIX_REGEX = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)


def expandvars(worker, path):
    if worker.platform == 'Windows':
        return _expandvars_windows(worker, path)
    else:
        return _expandvars_posix(worker, path)


def _expandvars_posix(worker, path):
    """ expandvars for Linux and Mac OS. """
    if '$' not in path:
        return path
    start = '{'
    end = '}'
    i = 0
    while True:
        m = _VARS_POSIX_REGEX.search(path, i)
        if not m:
            break
        i, j = m.span(0)
        name = m.group(1)
        if name.startswith(start) and name.endswith(end):
            name = name[1:-1]
        try:
            value = worker.environment[name]
        except KeyError:
            i = j
        else:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail
    return path


def _expandvars_windows(worker, path):
    """ expandvars for Windows. """
    if '$' not in path and '%' not in path:
        return path

    varchars = string.ascii_letters + string.digits + '_-'
    quote = '\''
    percent = '%'
    brace = '{'
    rbrace = '}'
    dollar = '$'

    res = path[:0]
    index = 0
    pathlen = len(path)

    while index < pathlen:
        c = path[index:index + 1]
        if c == quote:
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index(c)
                res += c + path[:index + 1]
            except ValueError:
                res += c + path
                index = pathlen - 1
        elif c == percent:
            if path[index + 1:index + 2] == percent:
                res += c
                index += 1
            else:
                path = path[index + 1:]
                pathlen = len(path)
                try:
                    index = path.index(percent)
                except ValueError:
                    res += percent + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        value = worker.environment[var]
                    except KeyError:
                        value = percent + var + percent
                    res += value
        elif c == dollar:
            if path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            elif path[index + 1:index + 2] == brace:
                path = path[index + 2:]
                pathlen = len(path)
                try:
                    index = path.index(rbrace)
                except ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        value = worker.environment[var]
                    except KeyError:
                        value = dollar + brace + var + rbrace
                    res += value
            else:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                while c and c in varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                try:
                    value = worker.environment[var]
                except KeyError:
                    value = dollar + var
                res += value
                if c:
                    index -= 1
        else:
            res += c
        index += 1
    return res