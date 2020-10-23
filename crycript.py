from argparse import ArgumentParser
from base64 import urlsafe_b64encode
from getpass import getpass
from os import remove, urandom
from os.path import isfile, abspath
from time import sleep

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# GLOBAL VARIABLES
# str: encrypted file extension
EXTENSION = '.cry'
# int: key iterations
PBKDF_ITERATIONS = 100_000
# int: salt size
SALT_SIZE = 16
# b str: separator
SEPARATOR = b';'
# b str: crycript version
VERSION = b'CRYCRIPT:2020.10.22'
# b str: version key (this will be changing between each version)
VERSION_KEY = b'xCHACSdlbmg56i212CYyZrvl2weByLedxt7i3KitWS0='
# int: password length
PASSWORD_LENGTH = 6


# ERRORS
class Error(Exception): pass
class PathError(Error): pass
class PasswordError(Error): pass
class VersionError(Error): pass
class ArgumentError(Error): pass


def get_key(salt=None):
    # Get password
    password = getpass('Enter your password: ')
    if not password == getpass('Confirm password: ') and password >= PASSWORD_LENGTH:
        raise PasswordError('Passwords do not match.')

    # Change password string to binary string
    password = password.encode()

    # Salt
    if salt is None:
        salt = urandom(SALT_SIZE)

    # PBKDF2 function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=PBKDF_ITERATIONS,
        backend=default_backend()
    )

    # 'Translate' key
    key = urlsafe_b64encode(kdf.derive(password))

    # Delete password from memory
    del password

    return salt, key


def encrypt(path):
    if isfile(path) and not path.endswith(EXTENSION):
        # Always work with absolute path
        path = abspath(path)

        # Path for the encrypted file
        path_encrypted = path + EXTENSION

        # Get encryption key
        salt, key = get_key()

        # Set the cipher
        cipher = Fernet(key)

        # Set version key cipher
        version_cipher = Fernet(VERSION_KEY)

        # Read the original file and extract its contents
        with open(path, 'rb') as raw_file:
            contents = raw_file.read()

        # Encrypt contents
        contents = cipher.encrypt(contents)

        # Version key encryption
        salt = version_cipher.encrypt(salt)
        contents = version_cipher.encrypt(contents)

        # Write a new encrypted file
        with open(path_encrypted, 'wb') as encrypted_file:
            encrypted_file.write(VERSION + SEPARATOR + salt + SEPARATOR + contents)

        # Delete contents (encrypted) from memory
        del contents

        # Delete old file
        remove(path)

    elif not isfile(path):
        raise PathError('Encryption aborted: path is not a file.')

    elif path.endswith(EXTENSION):
        raise PathError(f'Encryption aborted: path is already encrypted.')


def decrypt(path):
    if isfile(path) and path.endswith(EXTENSION):
        # Always work with absolute path
        path = abspath(path)

        # Path for the encrypted file
        path_decrypted = path[: -1 * len(EXTENSION)]

        # Extract the encrypted content
        with open(path, 'rb') as encrypted_file:
            version, salt, contents = encrypted_file.read().split(SEPARATOR)

        # Make sure encrypted file is compatible with crycript version
        if version != VERSION:
            raise VersionError('Your encrypted file version is not supported.')

        # Delete version from memory
        del version

        # Set version key cipher
        version_cipher = Fernet(VERSION_KEY)

        # Version decrypt contents
        salt = version_cipher.decrypt(salt)
        contents = version_cipher.decrypt(contents)

        # Get decryption key
        salt, key = get_key(salt)

        # Delete salt from memory
        del salt

        # Set the cipher
        cipher = Fernet(key)

        try:
            # Decrypt contents
            contents = cipher.decrypt(contents)

        except InvalidToken:
            sleep(5)
            raise InvalidToken('Decryption aborted: invalid password.')

        # Write a new decrypted file
        with open(path_decrypted, 'wb') as decrypted_file:
            decrypted_file.write(contents)

        # Delete contents (decrypted) from memory
        del contents

        # Delete encrypted file
        remove(path)

    elif not isfile(path):
        raise PathError(f'Decryption aborted: path is not a file.')

    elif not path.endswith(EXTENSION):
        raise PathError(f'Decryption aborted: path is not encrypted.')


if __name__ == '__main__':
    parser = ArgumentParser(description='Custom python Fernet symmetric encryption tool by Salvador BG')
    parser.add_argument('path', help='path to file.')

    action = parser.add_mutually_exclusive_group()
    action.add_argument('-e', '--encrypt', help='encrypt a file.', action='store_true')
    action.add_argument('-d', '--decrypt', help='decrypt a file.', action='store_true')

    args = parser.parse_args()

    if (args.encrypt and args.decrypt) or (not args.encrypt and not args.decrypt):
        raise ArgumentError('You need to choose one action (either encrypt or decrypt).')

    elif args.encrypt:
        encrypt(args.path)

    elif args.decrypt:
        decrypt(args.path)

    else:
        raise ArgumentError('How the fuck did you ended here?')
