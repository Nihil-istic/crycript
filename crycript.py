#!shebang

from argparse import ArgumentParser
from base64 import urlsafe_b64encode
from getpass import getpass
from os import remove, urandom
from os.path import isfile, abspath, dirname

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
VERSION = b'CRYCRIPT:2020.11.20'
# str: DO NOT TOUCH THIS ONE, string version of VERSION
STR_VERSION = str(VERSION)[2:-1]
# b str: version key (this will be changing between each version)
VERSION_KEY = b'O87XjL67TLJP3pNa-YRCDQuR2DYTHGiy67m__-JPRbM='
# int: password length
PASSWORD_LENGTH = 8


def bye(text):
    print(text)
    raise SystemExit


def get_key(salt=None):
    # Get password
    password = getpass('Enter your password: ')

    # Check for length of password
    if len(password) < PASSWORD_LENGTH:
        bye(f'Password must be at least {PASSWORD_LENGTH} characters.')

    # Check to see if there is no typo in password
    if not password == getpass('Confirm password: '):
        bye('Passwords do not match.')

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

        # File name
        path_filename = path[1 + len(dirname(path)):].encode()

        # Path for the encrypted file
        path_encrypted = dirname(path) + '/' + str(Fernet.generate_key())[2:-1] + EXTENSION

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
        path_filename = cipher.encrypt(path_filename)

        # Version key encryption
        salt = version_cipher.encrypt(salt)
        contents = version_cipher.encrypt(contents)
        path_filename = version_cipher.encrypt(path_filename)

        # Write a new encrypted file
        with open(path_encrypted, 'wb') as encrypted_file:
            encrypted_file.write(VERSION + SEPARATOR + salt + SEPARATOR + path_filename + SEPARATOR + contents)

        # Delete contents (encrypted) from memory
        del contents

        # Delete old file
        remove(path)

    elif not isfile(path):
        bye('Encryption aborted: path is not a file.')

    elif path.endswith(EXTENSION):
        bye(f'Encryption aborted: path is already encrypted.')


def decrypt(path):
    if isfile(path) and path.endswith(EXTENSION):
        # Always work with absolute path
        path = abspath(path)

        # Extract the encrypted content
        with open(path, 'rb') as encrypted_file:
            version, salt, path_decrypted, contents = encrypted_file.read().split(SEPARATOR)

        # Make sure encrypted file is compatible with crycript version
        if version != VERSION:
            bye(f'Your encrypted file version is not supported.')

        # Delete version from memory
        del version

        # Set version key cipher
        version_cipher = Fernet(VERSION_KEY)

        # Version decrypt contents
        salt = version_cipher.decrypt(salt)
        contents = version_cipher.decrypt(contents)
        path_decrypted = version_cipher.decrypt(path_decrypted)

        # Get decryption key
        salt, key = get_key(salt)

        # Delete salt from memory
        del salt

        # Set the cipher
        cipher = Fernet(key)

        try:
            # Decrypt contents
            contents = cipher.decrypt(contents)

            # Decrypt filename
            path_decrypted = cipher.decrypt(path_decrypted)

        except InvalidToken:
            bye('Decryption aborted: invalid password.')

        # Write a new decrypted file
        path_decrypted = dirname(path) + '/' + path_decrypted.decode()
        with open(path_decrypted, 'wb') as decrypted_file:
            decrypted_file.write(contents)

        # Delete contents (decrypted) from memory
        del contents

        # Delete encrypted file
        remove(path)

    elif not isfile(path):
        bye(f'Decryption aborted: path is not a file.')

    elif not path.endswith(EXTENSION):
        bye(f'Decryption aborted: path is not encrypted.')


if __name__ == '__main__':
    # Set parser
    parser = ArgumentParser(description='Python symmetric encryption tool by Salvador BG')

    # Set version
    parser.add_argument('-v', '--version', help='show version and exit', action='version', version=STR_VERSION)

    # Set path argument
    parser.add_argument('path', help='path to file')

    # Set mutually exclusive action (either encrypt or decrypt)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-e', '--encrypt', help='encrypt a file', action='store_true')
    action.add_argument('-d', '--decrypt', help='decrypt a file', action='store_true')

    # Parse arguments
    args = parser.parse_args()

    # Make sure only one argument is given
    if (args.encrypt and args.decrypt) or (not args.encrypt and not args.decrypt):
        bye('You need to choose one action (either encrypt or decrypt).')

    # Encrypt action
    elif args.encrypt:
        encrypt(args.path)
        bye('Encryption completed.')

    # Decrypt action
    elif args.decrypt:
        decrypt(args.path)
        bye('Decryption completed.')

    # What the fuck?
    else:
        bye('How the fuck did you ended here?')
