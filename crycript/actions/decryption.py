from os import remove, listdir
from os.path import dirname, join as os_join, basename
from random import choice
from time import sleep, time

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from tqdm import tqdm

from crycript import constants, utils


def decrypt(path: str, key: bytes = None) -> str:
    """Decrypts an encrypted crycript file:

    path: str -> absolute path to encrypted crycript file
    key: bytes -> valid cryptography.fernet.Fernet key

    Encrypted file structure: [] represents a file line

    [Encryption version (YYYY.MM.DD)]
    [Fernet keys used for decryption, encrypted using the key generated with password_to_key()]
    [Encrypted original filename]
    [Encrypted contents 1]
    [Encrypted contents 2]
    [Encrypted contents 3]
    ...
    [Encrypted contents n-2]
    [Encrypted contents n-1]
    [Encrypted contents n]

    Where n is file size (in bytes) divided by crycript.constants.ENCRYPTION_BUFFER_SIZE, rounded up with math.ceil"""

    if type(key) != bytes:
        key_cipher = Fernet(utils.password_to_key(confirm_password=False, generate_token=False))
    else:
        try:
            key_cipher = Fernet(key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    start = time()

    filename = basename(path)
    parent_dir = dirname(path)

    with open(path, 'rb') as original_file:
        original_file.readline()

        try:
            file_keys = tuple(key_cipher.decrypt(original_file.readline()[:-1]).split(b' '))
        except InvalidToken:
            sleep(constants.INVALID_PASSWORD_DELAY)
            utils.kill('Aborted: invalid password')

        try:
            file_ciphers = tuple(Fernet(key) for key in file_keys)
        except (ValueError, Exception):
            utils.kill('Aborted: key block was replaced')

        del file_keys
        del key_cipher

        try:
            new_filename = file_ciphers[0].decrypt(original_file.readline()[:-1]).decode()
        except InvalidToken:
            utils.kill('Aborted: filename block was replaced')

        while new_filename in listdir(parent_dir):
            new_filename = choice(constants.ENCRYPTED_FILENAME_CHARSET) + new_filename

        with open(os_join(parent_dir, new_filename), 'wb') as decrypted_file:
            for line, cipher in enumerate(tqdm(
                    file_ciphers[1:],
                    desc=filename,
                    leave=False,
                    dynamic_ncols=True
            )):
                try:
                    decrypted_file.write(
                        cipher.decrypt(
                            original_file.readline()[:-1]
                        )
                    )
                except InvalidToken:
                    remove(os_join(parent_dir, new_filename))
                    utils.kill(f'Aborted: encrypted block line {line + 4} was modified')

    if not constants.PRESERVE_ORIGINAL_FILES:
        remove(path)

    if new_filename.endswith(constants.TAR_GZ_FILE_EXTENSION):
        utils.tar_gz_to_directory(os_join(parent_dir, new_filename), parent_dir)
        new_filename = new_filename[:-1 * len(constants.TAR_GZ_FILE_EXTENSION)]

    end = time()

    return f'{filename} -> {new_filename} in {round((end - start), 4)} seconds'
