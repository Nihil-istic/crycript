import base64
import getpass
import os
import tarfile
import time
import secrets

import cryptography
import cryptography.fernet
import cryptography.hazmat
import cryptography.hazmat.primitives
import cryptography.hazmat.primitives.hashes
import cryptography.hazmat.primitives.kdf
import cryptography.hazmat.primitives.kdf.pbkdf2

import crycript_globals


def kill(txt: str, delay: bool = False):
    print(txt)

    if delay:
        input('Press enter to exit')

    raise SystemExit


def delete_dir(dir_to_delete: str):
    for root, dirs, files in os.walk(dir_to_delete, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(dir_to_delete)


def dir_to_tar_gz(input_dir: str, output_tar: str):
    with tarfile.open(output_tar, 'w:gz') as tar:
        tar.add(input_dir, arcname=os.path.basename(input_dir))
    delete_dir(input_dir)


def tar_gz_to_dir(input_tar: str, output_dir: str):
    with tarfile.open(input_tar, 'r:gz') as tar:
        tar.extractall(members=tar.getmembers(), path=output_dir)
    os.remove(input_tar)


def password_to_key(confirm_password: bool, password: str = None,
                    password_message: str = 'password: ', confirmation_message: str = 'repeat password: ') -> bytes:
    if password is None:
        password = getpass.getpass(password_message)

        if confirm_password:
            if getpass.getpass(confirmation_message) != password:
                kill('Aborted: passwords do not match')

    if len(password) < crycript_globals.MINIMUM_PASSWORD_LENGTH:
        kill(f'Aborted: password should be at least {crycript_globals.MINIMUM_PASSWORD_LENGTH} characters')

    salt = password[0] + password[::-1] + password[-1] + str(len(password))

    kdf = cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC(
        algorithm=cryptography.hazmat.primitives.hashes.SHA512(),
        length=32,
        salt=salt.encode(),
        iterations=crycript_globals.PBKDF2_ITERATIONS,
        backend=cryptography.hazmat.backends.default_backend()
    )

    return base64.urlsafe_b64encode(
        kdf.derive(
            password.encode()
        )
    )


def encrypt(path: str) -> str:
    if path.endswith(crycript_globals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file already encrypted')

    try:
        key_encryptor = cryptography.fernet.Fernet(password_to_key(True))
    except (KeyboardInterrupt, EOFError):
        raise SystemExit

    clock_start = time.time()

    key = cryptography.fernet.Fernet.generate_key()

    file_encryptor = cryptography.fernet.Fernet(key)

    encrypted_key = key_encryptor.encrypt(key)
    for _ in range(crycript_globals.KEY_ENCRYPTION_ITERATIONS - 1):
        encrypted_key = key_encryptor.encrypt(encrypted_key)

    del key_encryptor, key

    if os.path.isdir(path):
        try:
            dir_to_tar_gz(path, path + '.tar.gz')
        except PermissionError:
            try:
                os.remove(path + '.tar.gz')
            except FileNotFoundError:
                pass
            kill('Aborted: the directory and the files it contains must have read permissions')
        path += '.tar.gz'

    path_dirname = os.path.dirname(path)

    path_filename = path[len(path_dirname) + 1:]
    path_filename_encrypted = file_encryptor.encrypt(path_filename.encode())

    while True:
        path_filename_new = path_filename[:crycript_globals.ENCRYPTED_FILENAME_ORIGINAL_CHARS]
        path_filename_new += '-'
        path_filename_new += ''.join(
            [secrets.choice(crycript_globals.ENCRYPTED_FILENAME_CHARSET)
             for _ in range(
                crycript_globals.ENCRYPTED_FILENAME_RANDOM_CHARS
            )]
        )
        path_filename_new += crycript_globals.ENCRYPTED_FILE_EXTENSION

        if path_filename_new not in os.listdir(path_dirname):
            break

    with open(os.path.join(path_dirname, path_filename_new), 'wb') as encrypted_file:
        encrypted_file.write(crycript_globals.BYTES_VERSION)
        encrypted_file.write(b'\n')

        encrypted_file.write(encrypted_key)
        encrypted_file.write(b'\n')

        encrypted_file.write(path_filename_encrypted)
        encrypted_file.write(b'\n')

    try:
        with open(path, 'rb') as original_file:
            while True:
                part = original_file.read(crycript_globals.ENCRYPTION_BUFFER_SIZE)

                if part == b'':
                    break

                encrypted_part = file_encryptor.encrypt(part)

                with open(os.path.join(path_dirname, path_filename_new), 'ab') as encrypted_file:
                    encrypted_file.write(encrypted_part)
                    encrypted_file.write(b'\n')
    except PermissionError:
        os.remove(os.path.join(path_dirname, path_filename_new))
        kill('Aborted: the file must have read permissions')

    with open(os.path.join(path_dirname, path_filename_new), 'ab') as encrypted_file:
        encrypted_file.write(crycript_globals.STOP_SIGNAL)
        encrypted_file.write(b'\n')

    os.remove(path)

    clock_end = time.time()

    return f'{path_filename} -> {path_filename_new} in {round(clock_end - clock_start, 4)} seconds'


def decrypt(path: str) -> str:
    if not path.endswith(crycript_globals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file not encrypted')

    if not os.path.isfile(path):
        kill('Aborted: path is not a file')

    clock_start = time.time()

    path_dirname = os.path.dirname(path)

    path_filename = path[len(path_dirname) + 1:]

    try:
        with open(path, 'rb') as encrypted_file:
            version = encrypted_file.readline()[:-1]

            if version != crycript_globals.BYTES_VERSION and version not in crycript_globals.SUPPORTED_VERSIONS:
                message = 'Aborted: invalid version:\n'
                message += f'crycript version: {crycript_globals.STRING_VERSION}\n'
                message += f'file version: {version}\n'
                message += f'other supported versions: {crycript_globals.SUPPORTED_VERSIONS}'
                kill(message)

            encrypted_key = encrypted_file.readline()[:-1]
            path_filename_new_encrypted = encrypted_file.readline()[:-1]
    except PermissionError:
        kill('Aborted: the file must have read permissions')

    clock_password_start = time.time()
    try:
        key_decryptor = cryptography.fernet.Fernet(password_to_key(False))
    except (KeyboardInterrupt, EOFError):
        raise SystemExit
    clock_password_end = time.time()

    try:
        key = key_decryptor.decrypt(encrypted_key)
    except cryptography.fernet.InvalidToken:
        time.sleep(crycript_globals.INVALID_PASSWORD_DELAY)
        kill('Aborted: invalid password')
    for _ in range(crycript_globals.KEY_ENCRYPTION_ITERATIONS - 1):
        key = key_decryptor.decrypt(key)

    file_decryptor = cryptography.fernet.Fernet(key)

    path_filename_new = file_decryptor.decrypt(path_filename_new_encrypted).decode()

    with open(path, 'rb') as encrypted_file:
        [encrypted_file.readline() for _ in range(3)]
        while True:
            encrypted_part = encrypted_file.readline()[:-1]

            if encrypted_part == crycript_globals.STOP_SIGNAL:
                break

            try:
                part = file_decryptor.decrypt(encrypted_part)
            except cryptography.fernet.InvalidToken:
                try:
                    os.remove(os.path.join(path_dirname, path_filename_new))
                except FileNotFoundError:
                    pass
                kill('Aborted: encrypted file was modified')

            with open(os.path.join(path_dirname, path_filename_new), 'ab') as decrypted_file:
                decrypted_file.write(part)

    os.remove(path)

    if path_filename_new.endswith('.tar.gz'):
        tar_gz_to_dir(os.path.join(path_dirname, path_filename_new), path_dirname)
        path_filename_new = path_filename_new[:-7]

    clock_end = time.time()

    return f'{path_filename} -> {path_filename_new} in ' \
           f'{round((clock_end - clock_start) - (clock_password_end - clock_password_start), 4)} seconds'


def change_password(path: str) -> str:
    if not path.endswith(crycript_globals.ENCRYPTED_FILE_EXTENSION):
        kill('Aborted: file not encrypted')

    if not os.path.isfile(path):
        kill('Aborted: path is not a file')

    clock_start = time.time()

    os.rename(path, path + '.tmp')

    clock_password_start = time.time()
    try:
        old_cipher = cryptography.fernet.Fernet(password_to_key(False, password_message='old password: '))
        new_cipher = cryptography.fernet.Fernet(password_to_key(True, password_message='new password: '))
    except (KeyboardInterrupt, EOFError):
        raise SystemExit
    clock_password_end = time.time()

    try:
        with open(path + '.tmp', 'rb') as old_file:
            with open(path, 'wb') as new_file:
                version = old_file.readline()[:-1]
                if version != crycript_globals.BYTES_VERSION and version not in crycript_globals.SUPPORTED_VERSIONS:
                    message = 'Aborted: invalid version:\n'
                    message += f'crycript version: {crycript_globals.STRING_VERSION}\n'
                    message += f'file version: {version}\n'
                    message += f'other supported versions: {crycript_globals.SUPPORTED_VERSIONS}'
                    kill(message)

                new_file.write(version)
                new_file.write(b'\n')

                encrypted_key = old_file.readline()[:-1]

                try:
                    key = old_cipher.decrypt(encrypted_key)
                except cryptography.fernet.InvalidToken:
                    os.rename(path + '.tmp', path)
                    time.sleep(crycript_globals.INVALID_PASSWORD_DELAY)
                    kill('Aborted: invalid password')
                for _ in range(crycript_globals.KEY_ENCRYPTION_ITERATIONS - 1):
                    key = old_cipher.decrypt(key)

                encrypted_key = new_cipher.encrypt(key)
                for _ in range(crycript_globals.KEY_ENCRYPTION_ITERATIONS - 1):
                    encrypted_key = new_cipher.encrypt(encrypted_key)

                new_file.write(encrypted_key)
                new_file.write(b'\n')

                while True:
                    part = old_file.readline()

                    new_file.write(part)

                    if part == crycript_globals.STOP_SIGNAL + b'\n':
                        break

    except PermissionError:
        kill('Aborted: the file must have read permissions')

    os.remove(path + '.tmp')

    clock_end = time.time()

    return 'Password updated successfully in '\
           f'{round((clock_end - clock_start) - (clock_password_end - clock_password_start),4)} seconds'
