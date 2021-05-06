from os import access, R_OK, W_OK, walk
from os.path import isdir, isfile, dirname, abspath, exists, isabs, join as os_join, basename

from .errors import kill
from .. import constants


def path_validator(paths: list, sort: bool = False, action: tuple = (False, False, False)) -> tuple:
    """Make sure a path:
    1) Is an absolute path
    2) Exists
    3) Is a file or a directory
    4) Has read and write permissions

    Then, depending on action tuple (encrypt, decrypt, change password),
    Make sure is a valid file

    paths: list -> list of strings of paths
    sort: bool -> sort new list before returning it if set to True"""

    new_paths = []
    new_filenames = []

    for path in paths:
        # Make path absolute
        if not isabs(path):
            path = abspath(path)

        filename = basename(path)

        if not exists(path):
            kill(f'Aborted: {filename}: path does not exist')

        if not isfile(path) and not isdir(path):
            kill(f'Aborted: {filename}: path is not a file or a directory')

        if not (access(path, R_OK) and access(path, W_OK)):
            kill(f'Aborted: {filename}: path must have read and write permissions')

        if not (access(dirname(path), R_OK) and access(dirname(path), W_OK)):
            kill(f'Aborted: {filename}: parent dir must have read and write permissions')

        if action[0]:
            # Check for encrypted file
            if path.endswith(constants.ENCRYPTED_FILE_EXTENSION):
                kill(f'Aborted: {filename}: file already encrypted')

            if isdir(path):
                for root, dirs, files in walk(path):

                    for d in dirs:
                        current = os_join(root, d)
                        if not (access(current, R_OK) and access(current, W_OK)):
                            kill(
                                f'Aborted: {filename}: everything inside must have read and write permissions')

                    for f in files:
                        current = os_join(root, f)
                        if not (access(current, R_OK) and access(current, W_OK)):
                            kill(
                                f'Aborted: {filename}: everything inside must have read and write permissions')

        elif action[1] or action[2]:
            # Check for unencrypted file
            if not path.endswith(constants.ENCRYPTED_FILE_EXTENSION):
                kill(f'Aborted: {filename}: file not encrypted')

            # Path must be a file
            if not isfile(path):
                kill(f'Aborted: {filename}: path is not a file')

            # Check file version
            with open(path, 'rb') as file:
                version = file.readline()[:-1]
                if version != constants.BYTES_VERSION:
                    message = f'Aborted: {filename}: invalid version\n'
                    message += f'crycript version: {constants.STRING_VERSION}\n'
                    message += f'file version: {version.decode()}'
                    kill(message)

        new_paths.append(path)
        new_filenames.append(filename)

    if sort:
        new_paths.sort()

    return new_paths, new_filenames
