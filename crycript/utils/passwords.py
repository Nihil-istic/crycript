from base64 import urlsafe_b64encode
from getpass import getpass
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits, punctuation
from time import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA3_512
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .errors import kill
from .. import constants


def new_token() -> str:
    """Returns a 6 digits string with the format: nn nn nn."""
    # Generate seed
    token = (time() * int(str(time())[:11:-1]))

    # Salt generation
    for i in range(constants.PBKDF2_ITERATIONS):
        token = (
                      token * ((time() % 1) + 1)
              ) % 1_000_000

    # Make sure there are 6 digits
    token = str(int(token)).zfill(6)

    return ' '.join(
        [token[:2],
         token[2:4],
         token[4:]]
    )


def token_validator(token: str) -> str:
    """Returns a properly formatted token, ignoring all non digit characters.

    token: str -> string to sanitize and format"""
    # Remove all non digits characters
    token = ''.join(char for char in token if char.isdigit())

    # Make sure there are 6 digits
    if len(token) != 6:
        kill('Aborted: invalid token format (six digits only)')

    return ' '.join(
        [str(token)[:2],
         str(token)[2:4],
         str(token)[4:]]
    )


def password_to_key(
        confirm_password: bool = True,
        generate_token: bool = True,
        password_message: str = 'Password: ',
        confirmation_message: str = 'Repeat Password: '
) -> bytes:
    """Returns a valid cryptography.fernet.Fernet key using PBKDF2 and SHA512.

    confirm_password: bool -> if set to True, ask for password twice and make sure they are identical
    generate_token: str -> generate a random token if True, ask for token if False
    password_message: str -> password prompt
    confirmation_message: str -> repeat password prompt"""
    # Use user input to get a password
    try:
        password = getpass(password_message).strip()
    except (KeyboardInterrupt, EOFError):
        # Raise exit on user ^C or ^D
        raise SystemExit

    # Verify password length
    if len(password) < constants.MINIMUM_PASSWORD_LENGTH or len(password) > constants.MAXIMUM_PASSWORD_LENGTH:
        kill(f'Aborted: password should be between {constants.MINIMUM_PASSWORD_LENGTH}'
             f' and {constants.MAXIMUM_PASSWORD_LENGTH} characters')

    # At least one lowercase
    if not any(char in lower for char in password):
        kill('Aborted: your password must have at least 1 lowercase')

    # At least one uppercase
    if not any(char in upper for char in password):
        kill('Aborted: your password must have at least 1 uppercase')

    # At least one number
    if not any(char in digits for char in password):
        kill('Aborted: your password must have at least 1 digit')

    # At least one special character
    if not any(char in punctuation for char in password):
        kill('Aborted: your password must have at least 1 of: ' + punctuation)

    # Ask for password twice
    if confirm_password:
        try:
            # Verify both passwords match
            if getpass(confirmation_message).strip() != password:
                kill('Aborted: passwords do not match')
        except (KeyboardInterrupt, EOFError):
            # Raise exit on user ^C or ^D
            raise SystemExit

    if generate_token:
        salt = new_token()
        print(f'Your token is: [{salt}] (put this somewhere safe)')
    else:
        try:
            salt = token_validator(getpass('Enter your token: '))
        except (KeyboardInterrupt, EOFError):
            # Raise exit on user ^C or ^D
            raise SystemExit

    # Set the key derivation function
    kdf = PBKDF2HMAC(
        algorithm=SHA3_512(),
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
