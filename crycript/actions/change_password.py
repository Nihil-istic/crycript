from os import rename
from os.path import basename, dirname, join as os_join
from time import sleep, time

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

from crycript import constants, utils


def change_password(path: str, old_key: bytes = None, new_key: bytes = None) -> str:
    """Changes the password_to_key() key, marked with >>> <<< in Encrypted file structure:

    path: str -> absolute path to encrypted crycript file
    old_key: bytes -> valid cryptography.fernet.Fernet key
    new_key: bytes -> valid cryptography.fernet.Fernet key

    Encrypted file structure: [] represents a file line

    [Encryption version (YYYY.MM.DD)]
    [Fernet keys used for decryption,>>> encrypted using the key generated with password_to_key() <<<]
    [Encrypted original filename]
    [Encrypted contents 1]
    [Encrypted contents 2]
    [Encrypted contents 3]
    ...
    [Encrypted contents n-2]
    [Encrypted contents n-1]
    [Encrypted contents n]

    Where n is file size (in bytes) divided by crycript.constants.ENCRYPTION_BUFFER_SIZE, rounded up with math.ceil"""
    if type(old_key) != bytes:
        old_cipher = Fernet(utils.password_to_key(
            confirm_password=False,
            password_message='Old Password: ',
            generate_token=False)
        )
    else:
        try:
            old_cipher = Fernet(old_key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    if type(new_key) != bytes:
        new_cipher = Fernet(utils.password_to_key(
            confirm_password=True,
            password_message='New Password: ')
        )
    else:
        try:
            new_cipher = Fernet(new_key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    start = time()

    with open(path, 'rb') as old_file:
        version = old_file.readline()

        try:
            encrypted_keys = new_cipher.encrypt(
                old_cipher.decrypt(
                    old_file.readline()[:-1]
                )
            )
        except InvalidToken:
            sleep(constants.INVALID_PASSWORD_DELAY)
            utils.kill('Aborted: invalid password')

        with open(path + constants.TEMPORAL_FILE_EXTENSION, 'wb') as new_file:
            new_file.write(version)

            new_file.write(encrypted_keys)
            new_file.write(b'\n')

            for line in old_file:
                new_file.write(line)

    if not constants.PRESERVE_ORIGINAL_FILES:
        rename(path + constants.TEMPORAL_FILE_EXTENSION, path)
        return f'Password updated in {round((time() - start), 4)} seconds'
    else:
        rename(path + constants.TEMPORAL_FILE_EXTENSION, os_join(dirname(path), 'new-' + basename(path)))
        return f'{basename(path)} -> {"new-" + basename(path)} in {round((time() - start), 4)} seconds'
