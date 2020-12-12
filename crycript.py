#!/usr/bin/env python

from base64 import urlsafe_b64encode
from getpass import getpass
from os import remove, listdir
from os.path import isfile, abspath, dirname
from secrets import choice
from time import time

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Encrypted file extension
EXTENSION: str = '.cry'

# Password iterations for key generation
PBKDF_ITERATIONS: int = 100_000

# Version of crycript
VERSION: bytes = b'CRYCRIPT:2020.12.12'

# String version, do not modify it
STR_VERSION: str = VERSION.decode()

# Interval for allowed password length
PASSWORD_LENGTH: tuple = (8, 128)

# Encryption filename length
FILENAME_LENGTH: int = 8

# Buffer size for file reading (1 = 1 byte), 1 Megabyte = 1_000_000
BUFFER: int = 10_000_000

# Stop signal (end of encrypted file)
STOP_SIGNAL: bytes = b'EOF'


def bye(text: str):  # Print text and exit
    print(text)
    raise SystemExit


def confusion():  # Show confusion and exit
    bye('How the fuck did you end up here?')


def get_filename():  # Generate random filename (for encrypted file)
    charset = 'ABCDEFGHIJKLNMOPQRSTUVWXYZabcdefghijklnmopqrstuvwxyz'
    new_filename = ''.join([choice(charset) for _ in range(FILENAME_LENGTH)]) + EXTENSION
    return new_filename


def get_key(confirm: bool):  # Generate a key from a given password
    # Get password
    password = getpass('Enter your password: ')

    # Check for length of password
    if len(password) < PASSWORD_LENGTH[0] or len(password) > PASSWORD_LENGTH[1]:
        bye(f'Password must be between {PASSWORD_LENGTH[0]} and {PASSWORD_LENGTH[1]} characters')

    # Password confirmation
    if confirm:
        if not password == getpass('Confirm password: '):
            bye('Passwords do not match')

    # Change password string to binary string
    password = password.encode()

    # PBKDF2 function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=b'',
        iterations=PBKDF_ITERATIONS,
        backend=default_backend()
    )

    # 'Translate' key
    key = urlsafe_b64encode(kdf.derive(password))

    # Delete password from memory
    del password

    # Return generated key
    return key


def encrypt(path: str, cipher: Fernet):  # Main encryption function
    if not path.endswith(EXTENSION):
        # Get start time
        clock_start = time()

        # Path for directory containing the file
        path_dir = dirname(path) + '/'

        # Original filename
        path_filename_old = path[len(path_dir):]

        while True:  # Make sure to generate a new and unique filename (to not overwrite files)
            # New filename
            path_filename_new = get_filename()

            if path_filename_new not in listdir(path_dir):
                break

        # Encrypted version of original filename
        path_filename_old_encrypted = cipher.encrypt(path_filename_old.encode())

        # Open new file (encrypted) to add version and original filename
        with open(path_dir + path_filename_new, 'wb') as file_encrypted:
            # Add crycript version
            file_encrypted.write(VERSION)
            file_encrypted.write(b'\n')

            # Encrypted filename
            file_encrypted.write(path_filename_old_encrypted)
            file_encrypted.write(b'\n')

        # Open original file and read its contents to start filling encrypted file
        with open(path, 'rb') as file_decrypted:
            while True:
                # Read a string stream with the size of BUFFER
                part_decrypted = file_decrypted.read(BUFFER)

                # If part_decrypted is b'' that means we reached the end of the file
                if part_decrypted == b'':
                    break

                # Encrypt contents
                part_encrypted = cipher.encrypt(part_decrypted)

                # Open encrypted file in append mode to add new encrypted content
                with open(path_dir + path_filename_new, 'ab') as file_encrypted:
                    # Encrypted content
                    file_encrypted.write(part_encrypted)
                    file_encrypted.write(b'\n')

        # After encrypting contents, append STOP_SIGNAL
        with open(path_dir + path_filename_new, 'ab') as file_encrypted:
            # End of file
            file_encrypted.write(STOP_SIGNAL)
            file_encrypted.write(b'\n')

        # Delete old (original) file
        remove(path)

        # Get end time
        clock_end = time()

        # Return clock
        return f'{path_filename_old} -> {path_filename_new} in {round(clock_end - clock_start, 4)} seconds'

    elif path.endswith(EXTENSION):
        bye('Aborted, file already encrypted')

    else:
        confusion()


def decrypt(path: str, cipher: Fernet):  # Main decryption function
    if path.endswith(EXTENSION):
        # Get start time
        clock_start = time()

        # Path to directory
        path_dir = dirname(path) + '/'

        # Original filename
        path_filename_old = path[len(path_dir):]

        # Open original (encrypted) file
        with open(path, 'rb') as file_encrypted:
            # Read version of the file encryption
            version = file_encrypted.readline()[:-1]

            # Check if versions match
            if version != VERSION:
                bye('Aborted, invalid crycript version')

            # Delete version
            del version

            path_filename_new_encrypted = file_encrypted.readline()[:-1]

            # Try to decrypt encrypted filename
            try:
                path_filename_new = cipher.decrypt(path_filename_new_encrypted)
            except InvalidToken:
                # If InvalidToken is raised, key is not the correct one
                bye('Aborted, invalid password')

            # Start to decrypt contents
            while True:
                # Get encrypted part
                part_encrypted = file_encrypted.readline()[:-1]

                # If part is equal to STOP_SIGNAL, stop
                if part_encrypted == STOP_SIGNAL:
                    break

                # Try to decrypt part
                try:
                    part_decrypted = cipher.decrypt(part_encrypted)
                except InvalidToken:
                    # If InvalidToken is raised, the file was probably modified
                    try:
                        remove(path_dir + path_filename_new.decode())
                    except FileNotFoundError:
                        pass
                    bye('Aborted, invalid password for part')

                # Append decrypted part to new file
                with open(path_dir + path_filename_new.decode(), 'ab') as file_decrypted:
                    file_decrypted.write(part_decrypted)

        # Remove old (encrypted) file
        remove(path)

        # Get end time
        clock_end = time()

        # Return clock
        return f'{path_filename_old} -> {path_filename_new.decode()} in {round(clock_end - clock_start, 4)} seconds'

    elif not path.endswith(EXTENSION):
        bye('Aborted, file is not encrypted')
    else:
        confusion()


if __name__ == '__main__':
    from argparse import ArgumentParser

    # Set parser
    parser = ArgumentParser(description='Python symmetric encryption tool by Salvador BG')

    # Set version
    parser.add_argument('--version', help='show version and exit', action='version', version=STR_VERSION)

    # Set path argument
    parser.add_argument('path', help='path to file')

    # Set mutually exclusive action (either encrypt or decrypt)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-e', '--encrypt', help='encrypt a file', action='store_true')
    action.add_argument('-d', '--decrypt', help='decrypt a file', action='store_true')

    # Parse arguments
    args = parser.parse_args()

    # Set absolute path
    args_path = abspath(args.path)

    # The script is designed to only work with files
    if not isfile(args_path):
        bye('Path is not a file')

    # Encrypt action
    if args.encrypt:
        encryption_cipher = Fernet(get_key(True))
        status = encrypt(args_path, encryption_cipher)
        bye(status)

    # Decrypt action
    elif args.decrypt:
        decryption_cipher = Fernet(get_key(False))
        status = decrypt(args_path, decryption_cipher)
        bye(status)

    # Action not selected
    else:
        bye('You need to enter at least one action [-e | -d]')
