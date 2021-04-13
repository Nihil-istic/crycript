from .action_imports import *


def encrypt(path: str, key: bytes = None) -> str:
    """Encrypts a file or directory

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

    path: str -> path to file or directory to encrypt
    key: bytes -> key for encrypting the file
    """

    if type(key) != bytes:
        try:
            # Get password based cipher
            key_encryptor = Fernet(utils.password_to_key())
        except (KeyboardInterrupt, EOFError):
            # Raise exit on user ^C or ^D
            raise SystemExit
    else:
        try:
            key_encryptor = Fernet(key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    # Start timer
    clock_start = time()

    # Get a encryption key
    key = Fernet.generate_key()

    # Set cipher
    file_encryptor = Fernet(key)

    # Encrypt key using password based cipher
    encrypted_key = key_encryptor.encrypt(key)

    if isdir(path):
        try:
            # Compress to .tar.gz file
            utils.path_to_tar_gz(path, path + constants.TAR_GZ_FILE_EXTENSION)
        except PermissionError:
            try:
                # Remove .tar.gz file if exists
                remove(path + constants.TAR_GZ_FILE_EXTENSION)
            except FileNotFoundError:
                pass

            utils.kill('Aborted: path must have read permissions')

        path += constants.TAR_GZ_FILE_EXTENSION

    # Get parent directory
    path_dirname = dirname(path)

    # Get filename
    path_filename = path[len(path_dirname) + 1:]

    # Encrypt filename
    path_filename_encrypted = file_encryptor.encrypt(path_filename.encode())

    # Generate a new filename
    while True:
        # Original filename chars
        if len(path_filename) >= constants.ENCRYPTED_FILENAME_ORIGINAL_CHARS:
            path_filename_new = path_filename[:constants.ENCRYPTED_FILENAME_ORIGINAL_CHARS]
        else:
            path_filename_new = path_filename

        # Separator between original filename chars and random chars
        path_filename_new += '-'

        # Random filename chars
        for _ in range(constants.ENCRYPTED_FILENAME_RANDOM_CHARS):
            path_filename_new += choice(constants.ENCRYPTED_FILENAME_CHARSET)

        # Crycript Extension
        path_filename_new += constants.ENCRYPTED_FILE_EXTENSION

        # Verify new filename does not exists
        if path_filename_new not in listdir(path_dirname):
            break

    try:
        # Create new encrypted file
        with open(os_join(path_dirname, path_filename_new), 'wb') as encrypted_file:
            # Add version
            encrypted_file.write(constants.BYTES_VERSION)
            encrypted_file.write(b'\n')

            # Add encrypted key
            encrypted_file.write(encrypted_key)
            encrypted_file.write(b'\n')

            # Add encrypted filename
            encrypted_file.write(path_filename_encrypted)
            encrypted_file.write(b'\n')
    except PermissionError:
        utils.tar_gz_to_directory(path, path_dirname)
        utils.kill('Aborted: the parent directory must have write permissions')

    try:
        # Open original file to read its contents
        with open(path, 'rb') as original_file:
            # Read original file in parts with the size of CrycriptGlobals.ENCRYPTION_BUFFER_SIZE
            while True:
                part = original_file.read(constants.ENCRYPTION_BUFFER_SIZE)

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
        utils.tar_gz_to_directory(path, path_dirname)
        utils.kill('Aborted: the file must have read permissions')

    # Remove original file
    remove(path)

    # Stop timer
    clock_end = time()

    if path_filename.endswith(constants.TAR_GZ_FILE_EXTENSION):
        path_filename = path_filename[: -1 * len(constants.TAR_GZ_FILE_EXTENSION)]

    # Return status
    return f'{path_filename} -> {path_filename_new}' \
           f' in {round(clock_end - clock_start, 4)} seconds'
