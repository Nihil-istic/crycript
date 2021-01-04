#!/usr/bin/env python

from base64 import urlsafe_b64encode
from getpass import getpass
from os import remove, listdir, rename
from os.path import isfile, abspath, dirname
from secrets import choice
from time import time

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Version of crycript
VERSION: bytes = b'CRYCRIPT:2021.01.03'

# Stop signal (end of encrypted file)
STOP_SIGNAL: bytes = b":'("

# String version, do not modify it
STR_VERSION: str = VERSION.decode()

# Encrypted file extension
EXTENSION: str = '.cry'

# Charset for filename generator
CHARSET: str = 'abcdefghijklnmopqrstuvwxyz'

# Password iterations for key generation
PBKDF_ITERATIONS: int = 100_000

# Key encryption iterations KEEP BETWEEN 1 AND 42, BIGGER NUMBERS WILL BE SLOWER
KEY_ITERATIONS: int = 28

# Encryption filename length
RANDOM_FILENAME_LENGTH: int = 8

# Original filename characters used in new filename
OLD_FILENAME_LENGTH: int = 2

# Buffer size for file reading (1 = 1 byte), 1 Megabyte = 1_000_000
BUFFER: int = 10_000_000

# Preserve original file
PRESERVE: bool = False

# Interval for allowed password length
PASSWORD_LENGTH: tuple = (8, 128)


def bye(text: str):  # Print text and exit
    print(text)
    raise SystemExit


def random_chars():  # Generate random string of chars (for encrypted file)
    return ''.join([choice(CHARSET) for _ in range(RANDOM_FILENAME_LENGTH)]) + EXTENSION


def get_key(confirm: bool, message: str = 'password: '):  # Generate a key from a given password
    # Get password
    password = getpass(message)

    # Check for length of password
    if len(password) < PASSWORD_LENGTH[0] \
            or len(password) > PASSWORD_LENGTH[1]:
        bye(f'Password must be between {PASSWORD_LENGTH[0]} and {PASSWORD_LENGTH[1]} characters')

    # Password confirmation
    if confirm:
        if not password == getpass('confirm password: '):
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
    if path.endswith(EXTENSION):
        bye('Aborted, file already encrypted')

    # Get start time
    clock_start = time()

    # Set encryption key
    decrypted_encryption_key = Fernet.generate_key()

    # Encrypted key
    encrypted_encryption_key = cipher.encrypt(decrypted_encryption_key)
    for _ in range(KEY_ITERATIONS-1):
        encrypted_encryption_key = cipher.encrypt(encrypted_encryption_key)

    # Set encryption cipher
    internal_cipher = Fernet(decrypted_encryption_key)

    # Delete cipher
    del cipher

    # Delete encryption key
    del decrypted_encryption_key

    # Path for directory containing the file
    path_dir = dirname(path) + '/'

    # Original filename
    path_filename_old = path[len(path_dir):]

    while True:  # Make sure to generate a new and unique filename (to not overwrite files)
        # New filename
        path_filename_new = path_filename_old[:OLD_FILENAME_LENGTH] + '-' + random_chars()

        if path_filename_new not in listdir(path_dir):
            break

    # Encrypted version of original filename
    path_filename_old_encrypted = internal_cipher.encrypt(path_filename_old.encode())

    # Open new file (encrypted) to add version and original filename
    try:
        with open(path_dir + path_filename_new, 'wb') as file_encrypted:
            # Add crycript version
            file_encrypted.write(VERSION)
            file_encrypted.write(b'\n')

            # Encrypted key
            file_encrypted.write(encrypted_encryption_key)
            file_encrypted.write(b'\n')

            # Encrypted filename
            file_encrypted.write(path_filename_old_encrypted)
            file_encrypted.write(b'\n')
    except PermissionError:
        bye(f'Aborted, you need to have write permissions for {path_dir + path_filename_new}')

    # Open original file and read its contents to start filling encrypted file
    try:
        with open(path, 'rb') as file_decrypted:
            while True:
                # Read a string stream with the size of BUFFER
                part_decrypted = file_decrypted.read(BUFFER)

                # If part_decrypted is b'' that means we reached the end of the file
                if part_decrypted == b'':
                    break

                # Encrypt contents
                part_encrypted = internal_cipher.encrypt(part_decrypted)

                # Open encrypted file in append mode to add new encrypted content
                with open(path_dir + path_filename_new, 'ab') as file_encrypted:
                    # Encrypted content
                    file_encrypted.write(part_encrypted)
                    file_encrypted.write(b'\n')

    except PermissionError:
        bye(f'Aborted, you need to have read permissions for {path_filename_old}')

    # After encrypting contents, append STOP_SIGNAL
    with open(path_dir + path_filename_new, 'ab') as file_encrypted:
        # End of file
        file_encrypted.write(STOP_SIGNAL)
        file_encrypted.write(b'\n')

    # Delete old (original) file
    if not PRESERVE:
        remove(path)

    # Get end time
    clock_end = time()

    # Return status
    return f'{path_filename_old} -> {path_filename_new} in {round(clock_end - clock_start, 4)} seconds'


def decrypt(path: str, cipher: Fernet):  # Main decryption function
    if not path.endswith(EXTENSION):
        bye('Aborted, file is not encrypted')

    # Get start time
    clock_start = time()

    # Path to directory
    path_dir = dirname(path) + '/'

    # Original filename
    path_filename_old = path[len(path_dir):]

    # Open original (encrypted) file
    try:
        with open(path, 'rb') as file_encrypted:
            # Read version of the file encryption
            version = file_encrypted.readline()[:-1]

            # Check if versions match
            if version != VERSION:
                bye('Aborted, invalid crycript version')

            # Delete version
            del version

            # Get encryption key
            encrypted_key = file_encrypted.readline()[:-1]

            # Get encrypted filename
            path_filename_new_encrypted = file_encrypted.readline()[:-1]

            try:
                # Get cipher
                decrypted_encrypted_key = cipher.decrypt(encrypted_key)
                for _ in range(KEY_ITERATIONS-1):
                    decrypted_encrypted_key = cipher.decrypt(decrypted_encrypted_key)
                internal_cipher = Fernet(decrypted_encrypted_key)
            except InvalidToken:
                # If InvalidToken is raised, key is not the correct one
                bye('Aborted, invalid password')

            # Delete variables no longer needed
            del cipher, encrypted_key, decrypted_encrypted_key

            # Decrypt filename
            path_filename_new = internal_cipher.decrypt(path_filename_new_encrypted)

            # Start to decrypt contents
            while True:
                # Get encrypted part
                part_encrypted = file_encrypted.readline()[:-1]

                # If part is equal to STOP_SIGNAL, stop
                if part_encrypted == STOP_SIGNAL:
                    break

                # Try to decrypt part
                try:
                    part_decrypted = internal_cipher.decrypt(part_encrypted)
                except InvalidToken:
                    # If InvalidToken is raised, the file was probably modified
                    try:
                        remove(path_dir + path_filename_new.decode())
                    except FileNotFoundError:
                        pass
                    bye('Aborted, encrypted file was modified')

                # Append decrypted part to new file
                try:
                    with open(path_dir + path_filename_new.decode(), 'ab') as file_decrypted:
                        file_decrypted.write(part_decrypted)
                except PermissionError:
                    bye(f'Aborted, you need to have read permissions for {path_dir + path_filename_new.decode()}')
    except PermissionError:
        bye(f'Aborted, you need to have read permissions for {path_filename_old}')

    # Delete old (original) file
    if not PRESERVE:
        remove(path)

    # Get end time
    clock_end = time()

    # Return status
    return f'{path_filename_old} -> {path_filename_new.decode()} in {round(clock_end - clock_start, 4)} seconds'


def change_password(path: str):  # Take an encrypted file, decrypt its internal key, encrypt it with a new password
    if not path.endswith(EXTENSION):
        bye('Aborted, file is not encrypted')

    # Rename old file
    rename(path, path + '.tmp')

    # Set cipher with the original password to decrypt encryption key
    old_cipher = Fernet(get_key(False, 'old password: '))

    # Set cipher with new password to encrypt encryption key
    new_cipher = Fernet(get_key(True, 'new password: '))

    # Open original file (moved to *.tmp)
    try:
        with open(path + '.tmp', 'rb') as old_file:

            # Open a new file with the original path
            try:
                with open(path, 'wb') as new_file:

                    # Parse crycript version
                    new_file.write(old_file.readline())

                    # Get encrypted encryption key
                    encrypted_encryption_key = old_file.readline()[:-1]

                    # Decrypt encrypted encryption key
                    try:
                        decrypted_encryption_key = old_cipher.decrypt(encrypted_encryption_key)
                    except InvalidToken:
                        rename(path + '.tmp', path)
                        bye('Aborted, invalid password')
                    for _ in range(KEY_ITERATIONS - 1):
                        decrypted_encryption_key = old_cipher.decrypt(decrypted_encryption_key)

                    # Delete old cipher
                    del old_cipher

                    # Delete encrypted encryption key
                    del encrypted_encryption_key

                    # Encrypt decrypted encryption key with new password
                    encrypted_encryption_key = new_cipher.encrypt(decrypted_encryption_key)
                    for _ in range(KEY_ITERATIONS - 1):
                        encrypted_encryption_key = new_cipher.encrypt(encrypted_encryption_key)

                    # Delete new cipher
                    del new_cipher

                    # Parse new encrypted encryption key to the file
                    new_file.write(encrypted_encryption_key)
                    new_file.write(b'\n')

                    # Parse all the following lines of the file
                    while True:
                        part = old_file.readline()
                        new_file.write(part)

                        # Stop when reached the end of the file
                        if part == STOP_SIGNAL + b'\n':
                            break
            except PermissionError:
                bye(f'Aborted, you need to have write permissions for {path}')
                rename(path + ".tmp", path)
    except PermissionError:
        bye(f'Aborted, you need to have read permissions for {path + ".tmp"}')

    if not PRESERVE:
        # Remove temporal location for original file
        remove(path + '.tmp')

    # Return status
    return 'Password updated successfully'


if __name__ == '__main__':
    from argparse import ArgumentParser

    # Set parser
    parser = ArgumentParser(description='Python symmetric encryption tool by Salvador BG')

    # Set version
    parser.add_argument(
        '-v',
        '--version',
        help='show version and exit',
        action='version',
        version=STR_VERSION)

    # Set path argument
    parser.add_argument(
        'path',
        help='path to file')

    # Set preserve value
    parser.add_argument(
        '-p',
        '--preserve',
        help='do not remove original file',
        action='store_true')

    # Set mutually exclusive action (either encrypt or decrypt)
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        '-e',
        '--encrypt',
        help='encrypt a file',
        action='store_true')

    action.add_argument(
        '-d',
        '--decrypt',
        help='decrypt a file',
        action='store_true')

    action.add_argument(
        '-c',
        '--change-password',
        dest='change_password',
        help='change the password of an encrypted file',
        action='store_true')

    # Parse arguments
    args = parser.parse_args()

    # Set absolute path
    args_path = abspath(args.path)

    # The script is designed to only work with files
    if not isfile(args_path):
        bye('Path is not a file')

    # Set preserve variable
    PRESERVE = args.preserve

    # Encrypt action
    if args.encrypt:
        encryption_cipher = Fernet(get_key(True))
        status = encrypt(args_path, encryption_cipher)
        del encryption_cipher
        bye(status)

    # Decrypt action
    elif args.decrypt:
        decryption_cipher = Fernet(get_key(False))
        status = decrypt(args_path, decryption_cipher)
        del decryption_cipher
        bye(status)

    # Change password action
    elif args.change_password:
        status = change_password(args_path)
        bye(status)

    # Action not selected
    else:
        bye('You need to enter at least one action [-e | -d]')
