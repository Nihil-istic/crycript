from .action_imports import *


def change_password(path: str, old_key: bytes = None, new_key: bytes = None) -> str:
    """Changes the key generated with password_to_key(), located in the line marked with <<<,
    all the other lines are not modified.

    Encrypted file structure: [] represents a file line

    [Encryption version (YYYY.MM.DD)]
    [Fernet key used for decryption, encrypted using the key generated with password_to_key()] <<<
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
    old_key: bytes -> original key of the file
    new_key: bytes -> new key that is going to replace the old one
    """

    if type(old_key) != bytes:
        try:
            old_cipher = Fernet(utils.password_to_key(
                confirm_password=False, password_message='Old Password: ',
                generate_pin=False))
        except (KeyboardInterrupt, EOFError):
            raise SystemExit
    else:
        try:
            old_cipher = Fernet(old_key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    if type(new_key) != bytes:
        try:
            new_cipher = Fernet(utils.password_to_key(confirm_password=True, password_message='New Password: '))
        except (KeyboardInterrupt, EOFError):
            raise SystemExit
    else:
        try:
            new_cipher = Fernet(new_key)
        except (ValueError, Exception):
            utils.kill('Aborted: key is invalid')

    # Start timer
    clock_start = time()

    try:
        # Open old file to read its contents
        with open(path, 'rb') as old_file:
            # Get Crycript version
            version = old_file.readline()[:-1]

            # Verify version
            if version != constants.BYTES_VERSION:
                utils.raise_invalid_version(version.decode())

            try:
                # Open new file to write contents
                with open(path + constants.TEMPORAL_FILE_EXTENSION, 'wb') as new_file:
                    # Write version to new file
                    new_file.write(version)
                    new_file.write(b'\n')

                    # Get encrypted key
                    encrypted_key = old_file.readline()[:-1]

                    try:
                        # Decrypt the encrypted key
                        key = old_cipher.decrypt(encrypted_key)
                    except InvalidToken:
                        sleep(constants.INVALID_PASSWORD_DELAY)
                        try:
                            remove(path + constants.TEMPORAL_FILE_EXTENSION)
                        except FileNotFoundError:
                            pass
                        utils.kill('Aborted: invalid password')

                    # Encrypt the key with the new password
                    encrypted_key = new_cipher.encrypt(key)

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
                utils.kill('Aborted: the parent directory must have write permissions')

    except PermissionError:
        utils.kill('Aborted: the file must have read permissions')

    # Remove old file
    rename(path + constants.TEMPORAL_FILE_EXTENSION, path)

    # Stop timer
    clock_end = time()

    # Return status
    return f'Password updated successfully in {round((clock_end - clock_start), 4)} seconds'
