from base64 import urlsafe_b64encode
from getpass import getpass
from os import walk, remove, rmdir, access, R_OK, W_OK
from os.path import isdir, isfile, join as os_join, basename, dirname, abspath, exists
from tarfile import open as tar_open
from time import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from . import constants


def kill(message: str, end: bool = True):
    """Print given message and then raise SystemExit.

    message: str -> message to print
    end: bool -> raise SystemExit if set to True"""
    # Print message
    print('\n', message, '\n', sep='')

    # Raise SystemExit (exit program)
    if end:
        raise SystemExit


def raise_invalid_version(version: str):
    message = 'Aborted: invalid version\n'
    message += f'Crycript version: {constants.STRING_VERSION}\n'
    message += f'File version: {version}'
    kill(message)


def path_validator(paths: list, sort: bool = True, action: tuple = (False, False, False)) -> tuple:
    """Make sure a path:
    1) Exists
    2) Is a file or a directory
    3) Is absolute
    4) Has read and write permissions

    Then, depending on action tuple (encrypt, decrypt, change password),
    Make sure is a valid file

    paths: list -> list of strings of paths
    sort: bool -> sort new list before returning it if set to True"""

    new_paths = []
    new_filenames = []

    for path in paths:
        filename = path[len(dirname(path)) + 1:]
        if not exists(path):
            kill(f'Aborted: {filename}: path does not exist')

        if not isfile(path) and not isdir(path):
            kill(f'Aborted: {filename}: path is not a file or a directory')

        if not (access(path, R_OK) and access(path, W_OK)):
            kill(f'Aborted: {filename}: path must have read and write permissions')

        if not (access(dirname(path), R_OK) and access(dirname(path), W_OK)):
            kill(f'Aborted: {filename}: parent dir must have read and write permissions')

        new_paths.append(abspath(path))

    if sort:
        new_paths.sort()

    for path in paths:
        filename = path[len(dirname(path)) + 1:]
        if action[0]:
            # Check for encrypted file
            if path.endswith(constants.ENCRYPTED_FILE_EXTENSION):
                kill(f'Aborted: {filename}: file already encrypted')

        elif action[1] or action[2]:
            # Check for unencrypted file
            if not path.endswith(constants.ENCRYPTED_FILE_EXTENSION):
                kill(f'Aborted: {filename}: file not encrypted')

            # Path must be a file
            if not isfile(path):
                kill(f'Aborted: {filename}: path is not a file')

        new_filenames.append(filename)

    return new_paths, new_filenames


def delete_directory(dir_to_delete: str):
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


def path_to_tar_gz(input_path: str, output_path: str):
    """Create a tar gz file based on the given directory, then remove the original directory.

    input_path: str -> path to compress
    output_path: str -> path to new tar gz file"""
    # Open a new tar gz file
    with tar_open(output_path, 'w:gz') as tar:
        # Add the contents of the directory to new tar gz file
        tar.add(input_path, arcname=basename(input_path))

    # Remove directory (now compressed as tar gz file)
    delete_directory(input_path)


def tar_gz_to_directory(input_tar_gz: str, output_directory: str):
    """Extract the given tar gz file in the given parent directory.

    input_tar_gz: str -> path to tar gz file to decompress
    output_directory: str -> path to parent directory for the extracted contents"""
    # Open the tar gz file
    with tar_open(input_tar_gz, 'r:gz') as tar:
        # Extract all its contents
        tar.extractall(members=tar.getmembers(), path=output_directory)

    # Remove tar gz file
    remove(input_tar_gz)


def password_to_key(
        confirm_password: bool = True,
        generate_pin: bool = True,
        password_message: str = 'Password: ',
        confirmation_message: str = 'Repeat Password: '
) -> bytes:
    """Returns a valid cryptography.fernet.Fernet key using PBKDF2 and SHA512.

    confirm_password: bool -> if set to True, ask for password twice and make sure they are identical
    generate_pin: str -> generate a random pin if True, ask for pin if False
    password_message: str -> password prompt
    confirmation_message: str -> repeat password prompt"""

    # Function to verify password strength
    def verify_password():
        # Verify password length
        if len(password) < constants.MINIMUM_PASSWORD_LENGTH or len(password) > constants.MAXIMUM_PASSWORD_LENGTH:
            kill(f'Aborted: password should be between {constants.MINIMUM_PASSWORD_LENGTH}'
                 f' and {constants.MAXIMUM_PASSWORD_LENGTH} characters')

        # Verify password complexity (ensures a bigger charset)
        # At least one lowercase
        if not any(char in 'abcdefghijklmnopqrstuvwxyz' for char in password):
            kill('Aborted: your password must have at least 1 lowercase')

        # At least one uppercase
        if not any(char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in password):
            kill('Aborted: your password must have at least 1 uppercase')

        # At least one number
        if not any(char in '0123456789' for char in password):
            kill('Aborted: your password must have at least 1 digit')

        # At least one special character
        if not any(char in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' for char in password):
            kill('Aborted: your password must have at least 1 of: ' + '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

    # Use user input to get a password
    password = getpass(password_message).strip()

    verify_password()

    # Ask for password twice
    if confirm_password:
        # Verify both passwords match
        if getpass(confirmation_message).strip() != password:
            kill('Aborted: passwords do not match')

    if generate_pin:
        # Generate salt seed based on given password
        salt = int(
            str(ord(password[0]))                       # First character
            + str(ord(password[len(password) // 2]))    # Middle character
            + str(ord(password[-1]))                    # Last character
            + str(len(password))                        # Length of the password
        )

        # Salt generation
        for i in range(constants.PBKDF2_ITERATIONS):
            salt = (
                           int(
                               salt * (time() % 1) * len(password) + 2 ** int(str(salt)[i % len(str(salt))])
                           ) % 900_000
                   ) + 100_000

        salt = str(salt)[:3] + ' ' + str(salt)[3:]
        print(f'Your pin is: [{salt}] (put this somewhere safe)')
    else:
        salt = getpass('Enter your pin: ').strip()

        if len(salt) != 7:
            kill('Aborted: pin is not valid, format for pin: [three digits, one space, three digits]')
        elif not all(salt[i].isdigit() for i in [0, 1, 2, 4, 5, 6]) \
                or salt[3] != ' ' or salt[0] == '0':
            kill('Aborted: pin is not valid, format for pin: [three digits, one space, three digits]')

    # Set the key derivation function
    kdf = PBKDF2HMAC(
        algorithm=SHA512(),
        length=32,
        salt=salt.encode(),
        iterations=constants.PBKDF2_ITERATIONS,
        backend=default_backend()
    )

    # Return a valid key
    return urlsafe_b64encode(
        kdf.derive(
            password.encode()
        )
    )
