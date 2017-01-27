""" Artisan security relies on the Fernet cipher and uses
PBKDF2HMAC with SHA256 for key derivation. """
import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..exceptions import IncorrectPassword


__all__ = [
    'create_key_from_password',
    'generate_key_and_salt_from_password',
    'encrypt_data',
    'decrypt_data'
]


def create_key_from_password(password, salt, exp_hash):
    """
    Creates a Fernet key from the password given.

    :param bytes password: Password given by the user.
    :param bytes salt: Salt that is stored.
    :param bytes exp_hash: Expected hash for the password.
    :return: Fernet key if the password is correct.
    :raises: `artisan.IncorrectPassword` if the password is not correct.
    """
    if not isinstance(password, bytes):
        password = password.encode('utf-8')
    assert isinstance(password, bytes)

    key_hash = _kdf(salt, 75000).derive(password)
    ver_hash = _kdf(salt, 75000).derive(key_hash)

    if ver_hash != exp_hash:
        raise IncorrectPassword()

    key = base64.urlsafe_b64encode(key_hash)
    return key


def generate_key_and_salt_from_password(password):
    """
    Generates a salt, hash, and key from a password.
    This function is to be used once when registering
    a new user for the Artisan server.

    :param bytes password: Password given by the user.
    :return: Fernet key, hash, and salt for the key.
    """
    if not isinstance(password, bytes):
        password = password.encode('utf-8')
    assert isinstance(password, bytes)

    salt = os.urandom(16)
    key_hash = _kdf(salt, 75000).derive(password)
    ver_hash = _kdf(salt, 75000).derive(key_hash)

    key = base64.urlsafe_b64encode(key_hash)
    return key, ver_hash, salt


def encrypt_data(key, data):
    """
    Encrypts data given a Fernet key.

    :param bytes key: Key generated via :meth:`artisan.fernet.create_key_from_password`.
    :param bytes data: Data to encrypt using the Fernet cipher.
    :return: Encrypted data as :class:`bytes`.
    """
    assert isinstance(data, bytes)
    fernet = Fernet(key)
    return fernet.encrypt(data)


def decrypt_data(key, data):
    """
    Decrypts data given a Fernet key.

    :param bytes key: Key generated via :meth:`artisan.fernet.create_key_from_password`.
    :param bytes data: Data to decrypt using the Fernet cipher.
    :return: Decrypted data as :class:`bytes`.
    """
    assert isinstance(data, bytes)
    fernet = Fernet(key)
    return fernet.decrypt(data)


def _kdf(salt, rounds):
    return PBKDF2HMAC(algorithm=hashes.SHA256(),
                      length=32,
                      salt=salt,
                      iterations=rounds,
                      backend=default_backend())
