from .action_imports import *


def decrypt(path: str, key: bytes = None) -> str:
    """Decrypts a file or directory

    Encrypted file structure: [] represents a file line

    [Encryption version (YYYY.MM.DD)]
    [Fernet key used for decryption, encrypted using the key generated with password_to_key()]
    [Encrypted original filename]
    [Encrypted contents 0]
    [Encrypted contents 1]
    [Encrypted contents 2]
    ...
    [Encrypted contents n-2]
    [Encrypted contents n-1]
    [Encrypted contents n]

    Where n is file size (in bytes) divided by crycript.constants.ENCRYPTION_BUFFER_SIZE, rounded up

    path: str -> path to a crycript file
    key: bytes -> key for decrypting the file
    """

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
            if version != constants.BYTES_VERSION:
                utils.raise_invalid_version(version.decode())

            # Get encrypted key
            encrypted_key = encrypted_file.readline()[:-1]

            # Get encrypted filename
            path_filename_new_encrypted = encrypted_file.readline()[:-1]

    except PermissionError:
        utils.kill('Aborted: the file must have read permissions')

    if type(key) != bytes:
        # Start password timer
        clock_password_start = time()
        try:
            # Get password based cipher
            key_decryptor = Fernet(utils.password_to_key(confirm_password=False, generate_pin=False))
        except (KeyboardInterrupt, EOFError):
            raise SystemExit
        # Stop password timer
        clock_password_end = time()
    else:
        clock_password_start, clock_password_end = 0, 0
        try:
            key_decryptor = Fernet(key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    try:
        # Decrypt the encrypted key
        key = key_decryptor.decrypt(encrypted_key)
    except InvalidToken:
        sleep(constants.INVALID_PASSWORD_DELAY)
        utils.kill('Aborted: invalid password')

    try:
        # Set cipher
        file_decryptor = Fernet(key)
    except (ValueError, Exception):
        utils.kill('Aborted: key was replaced')

    # Decrypt original filename
    path_filename_new = file_decryptor.decrypt(path_filename_new_encrypted).decode()

    # Generate a new filename if path_filename_new exists
    while path_filename_new in listdir(path_dirname):
        path_filename_new = choice(constants.ENCRYPTED_FILENAME_CHARSET) + path_filename_new

    # Create new decrypted file
    try:
        with open(os_join(path_dirname, path_filename_new), 'x') as _:
            pass
    except PermissionError:
        utils.kill('Aborted: parent directory must have write permissions')

    # Open encrypted file to read its contents
    with open(path, 'rb') as encrypted_file:
        # Skip the first 3 lines (version, key, filename)
        [encrypted_file.readline() for _ in range(3)]

        line = 3

        # Loop on encrypted contents
        while True:
            # Get encrypted file line
            encrypted_part = encrypted_file.readline()[:-1]

            # Break loop on the last line (end of file reached)
            if encrypted_part == b'':
                break

            line += 1

            try:
                # Decrypt line
                part = file_decryptor.decrypt(encrypted_part)
            except InvalidToken:
                try:
                    remove(os_join(path_dirname, path_filename_new))
                except FileNotFoundError:
                    pass
                utils.kill(f'Aborted: encrypted file line {line} was modified')

            # Add decrypted part to new file
            with open(os_join(path_dirname, path_filename_new), 'ab') as decrypted_file:
                decrypted_file.write(part)

    # Remove encrypted file
    remove(path)

    if path_filename_new.endswith(constants.TAR_GZ_FILE_EXTENSION):
        # Extract contents of new file
        utils.tar_gz_to_directory(os_join(path_dirname, path_filename_new), path_dirname)
        # Remove .tar.gz extension
        path_filename_new = path_filename_new[:-1 * len(constants.TAR_GZ_FILE_EXTENSION)]

    # Stop timer
    clock_end = time()

    # Return status
    return f'{path_filename} -> {path_filename_new} in ' \
           f'{round((clock_end - clock_start) - (clock_password_end - clock_password_start), 4)} seconds'
