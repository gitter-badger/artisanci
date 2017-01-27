import atexit
import os
import sys

import colorama
import toml

from .auth import (create_key_from_password,
                   generate_key_and_salt_from_password,
                   encrypt_data,
                   decrypt_data)
from .prompt import prompt_password, prompt_yes_or_no
from ..exceptions import IncorrectPassword


__all__ = [
    'parse_artisan_toml',
    'update_artisan_toml',
    'lock_artisan_toml',
    'unlock_artisan_toml',
    'create_artisan_toml'
]

_ENCRYPTED_TOKEN = b']encrypted['
_ARTISAN_TOML_LOCKED = False
_ARTISAN_TOML_KEY = None  # type: bytes
_ARTISAN_TOML_HASH = None  # type: bytes
_ARTISAN_TOML_SALT = None  # type: bytes
_DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.artisan.toml')
_SAFE_VALUE = '[[ THIS VALUE IS HIDDEN ]]'


def lock_artisan_toml(path=None):
    """ Locks the .artisan.lock files to prevent multiple
    artisan instances from running at once. """
    global _ARTISAN_TOML_LOCKED
    if not _ARTISAN_TOML_LOCKED:
        path = _default_artisan_toml(path)
        lock = os.path.join(os.path.dirname(path), '.artisan.lock')
        try:
            fd = os.open(lock, os.O_EXCL | os.O_CREAT | os.O_RDWR)
            os.close(fd)
            atexit.register(unlock_artisan_toml, path)
            _ARTISAN_TOML_LOCKED = True
        except (OSError, IOError):
            print(colorama.Fore.RED + 'Could not acquire the lock at `%s`'
                  '. Is Artisan open in another terminal?' % lock + colorama.Style.RESET_ALL)
            sys.exit(1)


def unlock_artisan_toml(path):
    """ Unlocks the .artisan.lock file. """
    global _ARTISAN_TOML_LOCKED
    if _ARTISAN_TOML_LOCKED:
        path = _default_artisan_toml(path)
        lock = os.path.join(os.path.dirname(path), '.artisan.lock')
        try:
            os.remove(lock)
        except (OSError, IOError):
            pass
        _ARTISAN_TOML_LOCKED = False


def parse_artisan_toml(path=None):
    path = _default_artisan_toml(path)
    lock_artisan_toml(path)
    try:
        with open(path, 'rb') as f:
            data = f.read()
            if data.startswith(_ENCRYPTED_TOKEN):
                data = data[len(_ENCRYPTED_TOKEN):]
                ver_hash = data[:32]
                salt = data[32:48]
                password = prompt_password('Enter your password to unlock `artisan.toml`')
                if not isinstance(password, bytes):
                    password = password.encode('utf-8')
                try:
                    key = create_key_from_password(password, salt, ver_hash)
                except IncorrectPassword:
                    print(colorama.Fore.LIGHTRED_EX + 'Password is not correct, could not open `artisan.toml`.')
                    sys.exit(1)
                data = decrypt_data(key, data[48:])

                global _ARTISAN_TOML_KEY
                global _ARTISAN_TOML_HASH
                global _ARTISAN_TOML_SALT
                _ARTISAN_TOML_KEY = key
                _ARTISAN_TOML_HASH = ver_hash
                _ARTISAN_TOML_SALT = salt

            conf = toml.loads(data.decode('utf-8'))
            print(colorama.Fore.LIGHTGREEN_EX + 'Artisan has loaded your `artisan.toml`.' + colorama.Style.RESET_ALL)
            return conf
    except (OSError, IOError):
        create_artisan_toml(path)


def update_artisan_toml(conf, path=None):
    path = _default_artisan_toml(path)
    lock_artisan_toml(path)
    with open(path, 'wb+') as f:
        data = toml.dumps(conf).encode('utf-8')
        if _ARTISAN_TOML_KEY is not None:
            assert isinstance(_ARTISAN_TOML_HASH, bytes)
            assert isinstance(_ARTISAN_TOML_SALT, bytes)
            data = encrypt_data(_ARTISAN_TOML_KEY, data)
            data = _ENCRYPTED_TOKEN + _ARTISAN_TOML_HASH + _ARTISAN_TOML_SALT + data
        f.write(data)


def create_artisan_toml(path=None):
    path = _default_artisan_toml(path)
    lock_artisan_toml(path)
    print('Creating a new `artisan.toml` file.')

    # Securely create the .artisan.toml file.
    try:
        fd = os.open(path, os.O_EXCL | os.O_CREAT | os.O_RDWR)
        os.fchmod(fd, 0o600)  # Set u+rw only on the file.
        os.close(fd)
    except (OSError, IOError) as e:
        print(colorama.Fore.LIGHTRED_EX + 'Could not securely create an `.artisan.toml` '
              'file at `%s`. Error: `%s`' % (path, os.strerror(e.errno)) + colorama.Style.RESET_ALL)
        sys.exit(1)

    password = ''
    while True:
        password = prompt_password('Enter a password to encrypt '
                                   'your artisan.toml. Leave empty if you wish '
                                   'to have no password:')
        if len(password) > 0:
            print(colorama.Fore.WHITE + 'Generating a new key for your artisan.toml...')
            key, ver_hash, salt = generate_key_and_salt_from_password(password)
            global _ARTISAN_TOML_KEY
            global _ARTISAN_TOML_HASH
            global _ARTISAN_TOML_SALT
            _ARTISAN_TOML_KEY = key
            _ARTISAN_TOML_HASH = ver_hash
            _ARTISAN_TOML_SALT = salt
            print(colorama.Fore.LIGHTGREEN_EX + 'A new key has been generated.')

        # Try to encourage users to encrypt their .artisan.toml file.
        elif not prompt_yes_or_no('Are you should you do not want a password? '
                                  'If you intend to use SSH workers without key-exchange '
                                  'your SSH passwords will be stored in plaintext. ',
                                  default=False):
            continue
        break

    update_artisan_toml(get_default_conf(len(password) > 0), path)
    print(colorama.Fore.LIGHTGREEN_EX + 'Created your `.artisan.toml` at `%s`' % path)

    # Give the user a helpful hint since it may be their first time.
    print(colorama.Fore.LIGHTCYAN_EX + 'Now run `artisan start'
          '%s`' % ('--path ' + path if path != _DEFAULT_PATH else '') +
          ' to start the Artisan daemon.')


def show_artisan_toml(path=None, safe=False):
    """ Decrypts and prints the .artisan.toml file """
    conf = parse_artisan_toml(path)
    if safe or prompt_yes_or_no('Are you sure you would like to '
                                'display your plaintext `artisan.toml` '
                                'file in the command line? Without the `--safe` '
                                'option active this file may contain sensitive '
                                'information.', False):
        if safe:
            for _, worker_conf in conf.get('worker', {}).items():
                if 'password' in worker_conf:
                    worker_conf['password'] = _SAFE_VALUE
                if 'pkey' in worker_conf:
                    worker_conf['pkey'] = _SAFE_VALUE
        sys.stderr.write(toml.dumps(conf))
    else:
        print(colorama.Fore.RED + 'Operation aborted by user.' + colorama.Style.RESET_ALL)
        sys.exit(1)


def get_default_conf(encrypted=False):
    """ Creates the default configuration
    for the artisan.toml file. """
    return {'worker': {'prhel7ac': {'host': 'prhel7ac',
                                    'type': 'ssh',
                                    'username': 'root',
                                    'password': 'rootpassword'}},
            'meta': {'encrypted': encrypted}}


def _default_artisan_toml(path=None):
    """ Gives the default path if no path is given. """
    if path is None:
        path = _DEFAULT_PATH
    return path
