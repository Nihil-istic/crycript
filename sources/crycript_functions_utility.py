from base64 import urlsafe_b64encode
from getpass import getpass
from secrets import choice

from crycript_globals import CHARSET, RANDOM_FILENAME_LENGTH, EXTENSION, PASSWORD_LENGTH, PBKDF_ITERATIONS
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def bye(text: str = ''):  # Print text and exit
    print(text)
    input('Press enter to exit ')
    raise SystemExit


def random_chars():  # Generate random string of chars (for encrypted file)
    return ''.join([choice(CHARSET) for _ in range(RANDOM_FILENAME_LENGTH)]) + EXTENSION


def get_key(confirm: bool, message: str = 'password: '):  # Generate a key from a given password
    try:
        # Get password
        password = getpass(message)

        # Check for length of password
        if len(password) < PASSWORD_LENGTH[0] \
                or len(password) > PASSWORD_LENGTH[1]:
            bye(f'Password must be between {PASSWORD_LENGTH[0]} and {PASSWORD_LENGTH[1]} characters')

        # Password confirmation
        if confirm:
            if not password == getpass('confirm password: '):
                bye('Passwords do not match')
    except KeyboardInterrupt:
        bye()
    except EOFError:
        bye()

    # Change password string to binary string
    password = password.encode()

    # PBKDF2 function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=b'',
        iterations=PBKDF_ITERATIONS,
        backend=default_backend()
    )

    # 'Translate' key
    key = urlsafe_b64encode(kdf.derive(password))

    # Delete password from memory
    del password

    # Return generated key
    return key
