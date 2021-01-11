# Version of crycript
VERSION: bytes = b'crycript 2021.01.11'

# Stop signal (end of encrypted file)
STOP_SIGNAL: bytes = b":'("

# String version, do not modify it
STR_VERSION: str = VERSION.decode()

# Encrypted file extension
EXTENSION: str = '.cry'

# Charset for filename generator
CHARSET: str = 'abcdefghijklnmopqrstuvwxyz'

# Password iterations for key generation
PBKDF_ITERATIONS: int = 100_000

# Key encryption iterations KEEP BETWEEN 1 AND 42, BIGGER NUMBERS WILL BE SLOWER
KEY_ITERATIONS: int = 28

# Encryption filename length
RANDOM_FILENAME_LENGTH: int = 8

# Original filename characters used in new filename
OLD_FILENAME_LENGTH: int = 2

# Buffer size for file reading (1 = 1 byte), 1 Megabyte = 1_000_000
BUFFER: int = 10_000_000

# Preserve original file
PRESERVE: bool = False

# Interval for allowed password length
PASSWORD_LENGTH: tuple = (8, 128)

# Width of interactive menu, should be greater or equal than 64
MENU_WIDTH: int = 64
