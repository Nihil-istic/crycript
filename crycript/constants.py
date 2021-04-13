BYTES_VERSION: bytes = b'2021.04.13'                                # Do not modify
STRING_VERSION: str = BYTES_VERSION.decode()                        # Do not modify

MINIMUM_PASSWORD_LENGTH: int = 8                                    # >= 8
MAXIMUM_PASSWORD_LENGTH: int = 1024                                 # > MINIMUM_PASSWORD_LENGTH, <= 4000
INVALID_PASSWORD_DELAY: float = 0.5                                 # >= 0.0

PBKDF2_ITERATIONS: int = 144_930                                    # >= 100_000

ENCRYPTED_FILENAME_ORIGINAL_CHARS: int = 2                          # >= 2
ENCRYPTED_FILENAME_RANDOM_CHARS: int = 6                            # >= 2
ENCRYPTED_FILENAME_CHARSET: str = 'abcdefghijklmnopqrstuvwxyz'      # Only a-z, A-Z, 0-9
ENCRYPTED_FILE_EXTENSION: str = '.cry'                              # Do not modify
TEMPORAL_FILE_EXTENSION: str = '.cry_t'                             # Do not modify
TAR_GZ_FILE_EXTENSION: str = '.cry_c'                               # Do not modify

ENCRYPTION_BUFFER_SIZE: int = 1_000_000                             # > 0, 1 equals 1 byte

