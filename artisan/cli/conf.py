import atexit
import os

import colorama
import toml


__all__ = [
    'parse_artisan_toml',
    'update_artisan_toml',
    'lock_artisan_toml',
    'unlock_artisan_toml'
]


def lock_artisan_toml(path=None):
    """ Locks the .artisan.lock files to prevent multiple
    artisan instances from running at once. """
    path = _default_artisan_toml(path)
    lock = os.path.join(os.path.dirname(path), '.artisan.lock')
    try:
        fd = os.open(lock, os.O_EXCL | os.O_CREAT | os.O_RDWR)
        os.close(fd)
        atexit.register(unlock_artisan_toml, path)
        return True
    except (OSError, IOError):
        print(colorama.Fore.RED + 'Could not acquire the lock at `%s`'
              '. Is Artisan open in another terminal?' % lock)
        return False


def unlock_artisan_toml(path):
    """ Unlocks the .artisan.lock file. """
    path = _default_artisan_toml(path)
    lock = os.path.join(os.path.dirname(path), '.artisan.lock')
    try:
        os.remove(lock)
    except (OSError, IOError):
        pass


def parse_artisan_toml(path=None):
    path = _default_artisan_toml(path)
    try:
        with open(path, 'r') as f:
            conf = toml.loads(f.read())
            return conf
    except (OSError, IOError):
        update_artisan_toml({}, path)


def update_artisan_toml(conf, path=None):
    path = _default_artisan_toml(path)
    with open(path, 'w+') as f:
        f.write(toml.dumps(conf))


def _default_artisan_toml(path=None):
    """ Gives the default path if no path is given. """
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.artisan.toml')
    return path
