BYTES_VERSION: bytes = b'2021.02.09'                                # Do not modify
STRING_VERSION: str = BYTES_VERSION.decode()                        # Do not modify

MINIMUM_PASSWORD_LENGTH: int = 8                                    # >= 8
INVALID_PASSWORD_DELAY: float = 0.5                                 # >= 0.0

PBKDF2_ITERATIONS: int = 114_857                                    # >= 100_000
KEY_ENCRYPTION_ITERATIONS: int = 27                                 # >= 0, <= 42

ENCRYPTED_FILENAME_ORIGINAL_CHARS: int = 2                          # >= 2
ENCRYPTED_FILENAME_RANDOM_CHARS: int = 6                            # >= 2
ENCRYPTED_FILENAME_CHARSET: str = 'abcdefghijklmnopqrstuvwxyz'      # Only alphanumeric
ENCRYPTED_FILE_EXTENSION: str = '.cry'                              # Do not modify

ENCRYPTION_BUFFER_SIZE: int = 1_000_000                             # >= 1_000_000, <= 100_000_000
