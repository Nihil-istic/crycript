from math import ceil
from os import remove, listdir
from os.path import isdir, dirname, join as os_join, getsize, basename
from random import choice
from time import time

from cryptography.fernet import Fernet
from tqdm import tqdm

from crycript import constants, utils


def encrypt(path: str, key: bytes = None) -> str:
    """Encrypts a file or directory:

    path: str -> absolute path to file or directory to encrypt
    key: bytes -> valid cryptography.fernet.Fernet key

    Encrypted file structure: [] represents a file line

    [Encryption version (YYYY.MM.DD)]
    [Fernet keys used for encryption, encrypted using the key generated with password_to_key()]
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
        key_cipher = Fernet(utils.password_to_key())
    else:
        try:
            key_cipher = Fernet(key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    start = time()

    filename = basename(path)
    parent_dir = dirname(path)

    compressed_filename = None
    compressed_path = None

    while True:
        if len(filename) >= constants.ENCRYPTED_FILENAME_ORIGINAL_CHARS:
            new_filename = filename[:constants.ENCRYPTED_FILENAME_ORIGINAL_CHARS]
        else:
            new_filename = filename

        new_filename += '-'

        for _ in range(constants.ENCRYPTED_FILENAME_RANDOM_CHARS):
            new_filename += choice(constants.ENCRYPTED_FILENAME_CHARSET)

        new_filename += constants.ENCRYPTED_FILE_EXTENSION

        if new_filename not in listdir(parent_dir):
            break

    if isdir(path):
        compressed_filename = filename + constants.TAR_GZ_FILE_EXTENSION
        compressed_path = path + constants.TAR_GZ_FILE_EXTENSION

        utils.path_to_tar_gz(path, compressed_path)

    working_path = compressed_path if compressed_path else path
    working_filename = compressed_filename if compressed_filename else filename

    rounds = ceil(getsize(working_path) / constants.ENCRYPTION_BUFFER_SIZE)

    file_keys = tuple(Fernet.generate_key() for _ in range(rounds + 1))

    file_ciphers = tuple(Fernet(key) for key in file_keys)

    encrypted_file_keys = key_cipher.encrypt(b' '.join(file_keys))
    del file_keys
    del key_cipher

    with open(working_path, 'rb') as original_file:
        with open(os_join(parent_dir, new_filename), 'ab') as encrypted_file:
            encrypted_file.write(constants.BYTES_VERSION)
            encrypted_file.write(b'\n')

            encrypted_file.write(encrypted_file_keys)
            encrypted_file.write(b'\n')

            encrypted_file.write(file_ciphers[0].encrypt(working_filename.encode()))
            encrypted_file.write(b'\n')

            for cipher in tqdm(
                    file_ciphers[1:],
                    desc=filename,
                    leave=False,
                    dynamic_ncols=True
            ):
                encrypted_file.write(
                    cipher.encrypt(
                        original_file.read(constants.ENCRYPTION_BUFFER_SIZE)
                    )
                )

                encrypted_file.write(b'\n')

    if compressed_path:
        remove(compressed_path)
    elif not constants.PRESERVE_ORIGINAL_FILES:
        remove(path)

    end = time()

    return f'{filename} -> {new_filename} in {round(end - start, 4)} seconds'
