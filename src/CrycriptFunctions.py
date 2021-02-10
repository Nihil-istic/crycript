from base64 import urlsafe_b64encode
from getpass import getpass
from os import walk, listdir, remove, rmdir, rename
from os.path import isdir, isfile, join as os_join, basename, dirname
from random import choice
from tarfile import open as tar_open
from time import time, sleep

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import CrycriptGlobals


def kill(message: str, delay: bool = False):
    """Print given message and then raise SystemExit.

    message: str -> message to print
    delay: bool -> wait for user input if set to True, then raise SystemExit"""
    # Print message
    print(message)

    # If delay, wait for user input before raising SystemExit
    if delay:
        input('Press enter to exit')

    # Raise SystemExit (exit program)
    raise SystemExit


def remove_directory(dir_to_delete: str):
    """Remove all the contents of a given directory, then remove it.

    dir_to_delete: str -> path to directory to delete"""
    # Loop on the contents of a directory from down to top
    for root, dirs, files in walk(dir_to_delete, topdown=False):

        # Loop on files
        for name in files:
            # Remove file
            remove(os_join(root, name))

        # Loop on directories
        for name in dirs:
            # Remove (empty) directory
            rmdir(os_join(root, name))

    # Remove (now empty) directory
    rmdir(dir_to_delete)


def directory_to_tar_gz(input_directory: str, output_tar_gz: str):
    """Create a .tar.gz file based on the given directory, then remove the original directory.

    input_directory: str -> path to directory to compress
    output_tar_gz: str -> path to new .tar.gz file"""
    # Open a new .tar.gz file
    with tar_open(output_tar_gz, 'w:gz') as tar:
        # Add the contents of the directory to new .tar.gz file
        tar.add(input_directory, arcname=basename(input_directory))

    # Remove directory (now compressed as .tar.gz file)
    remove_directory(input_directory)


def tar_gz_to_directory(input_tar_gz: str, output_directory: str):
    """Extract the given .tar.gz file in the given parent directory.

    input_tar_gz: str -> path to .tar.gz file to decompress
    output_directory: str -> path to parent directory for the extracted contents"""
    # Open the .tar.gz file
    with tar_open(input_tar_gz, 'r:gz') as tar:
        # Extract all its contents
        tar.extractall(members=tar.getmembers(), path=output_directory)

    # Remove .tar.gz file
    remove(input_tar_gz)


def password_to_key(confirm_password: bool = True, password: str = None,
                    password_message: str = 'password: ', confirmation_message: str = 'repeat password: ') -> bytes:
    """Returns a valid cryptography.fernet.Fernet key using PBKDF2 and SHA512.

    confirm_password: bool -> if set to True, ask for password twice and make sure they are identical
    password: str -> give a password instead of using user input
    password_message: str -> password prompt
    confirmation_message: str -> second password prompt"""

    # Function to verify password strength
    def verify_password():
        # Verify password length
        if len(password) < CrycriptGlobals.MINIMUM_PASSWORD_LENGTH:
            kill(f'Aborted: password should be at least {CrycriptGlobals.MINIMUM_PASSWORD_LENGTH} characters')

        # Verify password complexity (uses a bigger charset)
        if sum(a.islower() for a in password) < 1 \
                or sum(b.isupper() for b in password) < 1 \
                or sum(c.isdigit() for c in password) < 1 \
                or sum(not d.islower()
                       and not d.isupper()
                       and not d.isdigit()
                       and d.isprintable() for d in password) < 1:
            kill('Aborted: your password must have at least 1 lowercase, 1 uppercase, 1 number and 1 special character')

    # Use user input to get a password
    if type(password) != str:
        password = getpass(password_message)

        verify_password()

        # Ask for password twice
        if confirm_password:
            # Verify both passwords match
            if getpass(confirmation_message) != password:
                kill('Aborted: passwords do not match')
    else:
        verify_password()

    # Generate salt based on given password
    salt = password[0] + password[len(password) // 2] + password[-1] + str(len(password)).zfill(len(password) - 3)

    # Set the key derivation function
    kdf = PBKDF2HMAC(
        algorithm=SHA512(),
        length=32,
        salt=salt.encode(),
        iterations=CrycriptGlobals.PBKDF2_ITERATIONS,
        backend=default_backend()
    )

    # Return a valid key
    return urlsafe_b64encode(
        kdf.derive(
            password.encode()
        )
    )


def encrypt(path: str) -> str:
    """Encrypts a file or directory using the following structure: ([] represents a file line)

    [CrycriptGlobals.BYTES_VERSION]
    [Fernet key used for decryption, encrypted using the key generated with password_to_key()]
    [Encrypted original filename]
    [Encrypted contents] (as many parts as needed based on CrycriptGlobals.ENCRYPTION_BUFFER_SIZE and file size)
    [CrycriptGlobals.STOP_SIGNAL]

    path: str -> path to file or directory to encrypt, if path is directory, is compressed as .tar.gz and then encrypted
    """
    # Check for encrypted file
    if path.endswith(CrycriptGlobals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file already encrypted')

    try:
        # Get password based cipher
        key_encryptor = Fernet(password_to_key())
    except (KeyboardInterrupt, EOFError):
        # Raise exit on user ^C or ^D
        raise SystemExit

    # Start timer
    clock_start = time()

    # Get a encryption key
    key = Fernet.generate_key()

    # Set cipher
    file_encryptor = Fernet(key)

    # Encrypt key using password based cipher
    encrypted_key = key_encryptor.encrypt(key)
    for _ in range(CrycriptGlobals.KEY_ENCRYPTION_ITERATIONS - 1):
        encrypted_key = key_encryptor.encrypt(encrypted_key)

    # Check if path is directory
    if isdir(path):
        try:
            # Compress to .tar.gz file
            directory_to_tar_gz(path, path + '.tar.gz')
        except PermissionError:
            try:
                # Remove .tar.gz file if exists
                remove(path + '.tar.gz')
            except FileNotFoundError:
                pass

            kill('Aborted: the directory and the files it contains must have read permissions')

        path += '.tar.gz'

    # Get parent directory
    path_dirname = dirname(path)

    # Get filename
    path_filename = path[len(path_dirname) + 1:]

    # Encrypt filename
    path_filename_encrypted = file_encryptor.encrypt(path_filename.encode())

    # Generate a new filename
    while True:
        # Original filename chars
        if len(path_filename) >= CrycriptGlobals.ENCRYPTED_FILENAME_ORIGINAL_CHARS:
            path_filename_new = path_filename[:CrycriptGlobals.ENCRYPTED_FILENAME_ORIGINAL_CHARS]
        else:
            path_filename_new = path_filename

        # Separator between original filename chars and random chars
        path_filename_new += '-'

        # Random filename chars
        for _ in range(CrycriptGlobals.ENCRYPTED_FILENAME_RANDOM_CHARS):
            path_filename_new += choice(CrycriptGlobals.ENCRYPTED_FILENAME_CHARSET)

        # Crycript Extension
        path_filename_new += CrycriptGlobals.ENCRYPTED_FILE_EXTENSION

        # Verify new filename does not exists
        if path_filename_new not in listdir(path_dirname):
            break

    try:
        # Create new encrypted file
        with open(os_join(path_dirname, path_filename_new), 'wb') as encrypted_file:
            # Add version
            encrypted_file.write(CrycriptGlobals.BYTES_VERSION)
            encrypted_file.write(b'\n')

            # Add encrypted key
            encrypted_file.write(encrypted_key)
            encrypted_file.write(b'\n')

            # Add encrypted filename
            encrypted_file.write(path_filename_encrypted)
            encrypted_file.write(b'\n')
    except PermissionError:
        kill('Aborted: the parent directory must have write permissions')

    try:
        # Open original file to read its contents
        with open(path, 'rb') as original_file:
            # Read original file in parts with the size of CrycriptGlobals.ENCRYPTION_BUFFER_SIZE
            while True:
                part = original_file.read(CrycriptGlobals.ENCRYPTION_BUFFER_SIZE)

                # If True, end of file reached
                if part == b'':
                    break

                # Encrypt part
                encrypted_part = file_encryptor.encrypt(part)

                # Add encrypted part to encrypted file
                with open(os_join(path_dirname, path_filename_new), 'ab') as encrypted_file:
                    encrypted_file.write(encrypted_part)
                    encrypted_file.write(b'\n')

    except PermissionError:
        remove(os_join(path_dirname, path_filename_new))
        kill('Aborted: the file must have read permissions')

    # Remove original file
    remove(path)

    # Stop timer
    clock_end = time()

    # Return status
    return f'{path_filename} -> {path_filename_new} in {round(clock_end - clock_start, 4)} seconds'


def decrypt(path: str) -> str:
    """Decrypts a file or directory using the following structure: ([] represents a file line)

    [CrycriptGlobals.BYTES_VERSION]
    [Fernet key used for decryption, encrypted using the key generated with password_to_key()]
    [Encrypted original filename]
    [Encrypted contents] (as many parts as needed based on CrycriptGlobals.ENCRYPTION_BUFFER_SIZE and file size)
    [CrycriptGlobals.STOP_SIGNAL]

    path: str -> path to a crycript file
    """
    # Check for unencrypted file
    if not path.endswith(CrycriptGlobals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file not encrypted')

    # Path must be a Crycript file
    if not isfile(path):
        kill('Aborted: path is not a file')

    # Start timer
    clock_start = time()

    # Get parent directory
    path_dirname = dirname(path)

    # Get filename
    path_filename = path[len(path_dirname) + 1:]

    try:
        # Open encrypted file
        with open(path, 'rb') as encrypted_file:
            # Get file version
            version = encrypted_file.readline()[:-1]

            # Verify version
            if version != CrycriptGlobals.BYTES_VERSION:
                message = 'Aborted: invalid version\n'
                message += f'Crycript version: {CrycriptGlobals.STRING_VERSION}\n'
                message += f'File version: {version}\n'
                message += 'Go to https://github.com/Nihil-istic/crycript and download the right version'
                kill(message)

            # Get encrypted key
            encrypted_key = encrypted_file.readline()[:-1]

            # Get encrypted filename
            path_filename_new_encrypted = encrypted_file.readline()[:-1]

    except PermissionError:
        kill('Aborted: the file must have read permissions')

    # Start password timer
    clock_password_start = time()
    try:
        # Get password based cipher
        key_decryptor = Fernet(password_to_key(confirm_password=False))
    except (KeyboardInterrupt, EOFError):
        raise SystemExit
    # Stop password timer
    clock_password_end = time()

    try:
        # Decrypt first layer of encrypted key
        key = key_decryptor.decrypt(encrypted_key)
    except InvalidToken:
        sleep(CrycriptGlobals.INVALID_PASSWORD_DELAY)
        kill('Aborted: invalid password')
    # Decrypt remaining layers
    while len(key) > 44:
        key = key_decryptor.decrypt(key)
    if len(key) < 44:
        kill('Aborted: key was replaced')

    # Set cipher
    file_decryptor = Fernet(key)

    # Decrypt original filename
    path_filename_new = file_decryptor.decrypt(path_filename_new_encrypted).decode()

    # Generate a new filename if path_filename_new exists
    while path_filename_new in listdir(path_dirname):
        path_filename_new = choice(CrycriptGlobals.ENCRYPTED_FILENAME_CHARSET) + path_filename_new

    # Create new decrypted file
    try:
        with open(os_join(path_dirname, path_filename_new), 'x') as _:
            pass
    except PermissionError:
        kill('Aborted: parent directory must have write permissions')

    # Open encrypted file to read its contents
    with open(path, 'rb') as encrypted_file:
        # Skip the first 3 lines (version, key, filename)
        [encrypted_file.readline() for _ in range(3)]

        # Loop on encrypted contents
        while True:
            # Get encrypted file line
            encrypted_part = encrypted_file.readline()[:-1]

            # Break loop on the last line (end of file reached)
            if encrypted_part == b'':
                break

            try:
                # Decrypt line
                part = file_decryptor.decrypt(encrypted_part)
            except InvalidToken:
                try:
                    remove(os_join(path_dirname, path_filename_new))
                except FileNotFoundError:
                    pass
                kill('Aborted: encrypted file was modified')

            # Add decrypted part to new file
            with open(os_join(path_dirname, path_filename_new), 'ab') as decrypted_file:
                decrypted_file.write(part)

    # Remove encrypted file
    remove(path)

    # Extract contents if new file is a .tar.gz file
    if path_filename_new.endswith('.tar.gz'):
        tar_gz_to_directory(os_join(path_dirname, path_filename_new), path_dirname)
        # Remove .tar.gz extension
        path_filename_new = path_filename_new[:-7]

    # Stop timer
    clock_end = time()

    # Return status
    return f'{path_filename} -> {path_filename_new} in ' \
           f'{round((clock_end - clock_start) - (clock_password_end - clock_password_start), 4)} seconds'


def change_password(path: str) -> str:
    """Changes the password_to_key() key, located in the line marked with <<<, all the other lines are not modified.

    [CrycriptGlobals.BYTES_VERSION]
    [Fernet key used for decryption, encrypted using the key generated with password_to_key()] <<<
    [Encrypted original filename]
    [Encrypted contents] (as many parts as needed based on CrycriptGlobals.ENCRYPTION_BUFFER_SIZE and file size)
    [CrycriptGlobals.STOP_SIGNAL]

    path: str -> path to a crycript file
    """
    # Check for unencrypted file
    if not path.endswith(CrycriptGlobals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file not encrypted')

    # Path must be a Crycript file
    if not isfile(path):
        kill('Aborted: path is not a file')

    try:
        old_cipher = Fernet(password_to_key(confirm_password=False, password_message='old password: '))
        new_cipher = Fernet(password_to_key(password_message='new password: '))
    except (KeyboardInterrupt, EOFError):
        raise SystemExit

    # Start timer
    clock_start = time()

    # Move path to .tmp temporary location
    try:
        rename(path, path + '.tmp')
    except PermissionError:
        kill('Aborted: parent directory must have write permissions')

    try:
        # Open old file to read its contents
        with open(path + '.tmp', 'rb') as old_file:
            # Get Crycript version
            version = old_file.readline()[:-1]

            # Verify version
            if version != CrycriptGlobals.BYTES_VERSION:
                rename(path + '.tmp', path)
                message = 'Aborted: invalid version\n'
                message += f'Crycript version: {CrycriptGlobals.STRING_VERSION}\n'
                message += f'File version: {version}\n'
                message += 'Go to https://github.com/Nihil-istic/crycript and download the right version'
                kill(message)

            # Open new file to write contents
            with open(path, 'wb') as new_file:
                # Write version to new file
                new_file.write(version)
                new_file.write(b'\n')

                # Get encrypted key
                encrypted_key = old_file.readline()[:-1]

                try:
                    # Decrypt first layer of the key
                    key = old_cipher.decrypt(encrypted_key)
                except InvalidToken:
                    rename(path + '.tmp', path)
                    sleep(CrycriptGlobals.INVALID_PASSWORD_DELAY)
                    kill('Aborted: invalid password')
                # Decrypt remaining layers
                while len(key) > 44:
                    key = old_cipher.decrypt(key)
                if len(key) < 44:
                    kill('Aborted: key was replaced')

                # Encrypt first layer of the key with the new password
                encrypted_key = new_cipher.encrypt(key)
                for _ in range(CrycriptGlobals.KEY_ENCRYPTION_ITERATIONS - 1):
                    # Encrypt following layers
                    encrypted_key = new_cipher.encrypt(encrypted_key)

                # Write new encrypted key to new file
                new_file.write(encrypted_key)
                new_file.write(b'\n')

                # Add all the remaining parts to new file
                while True:
                    part = old_file.readline()

                    if part == b'':
                        break

                    new_file.write(part)

    except PermissionError:
        kill('Aborted: the file must have read permissions')

    # Remove old file
    remove(path + '.tmp')

    # Stop timer
    clock_end = time()

    # Return status
    return f'Password updated successfully in {round((clock_end - clock_start), 4)} seconds'
