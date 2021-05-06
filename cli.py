#!/usr/bin/env python3.9

from argparse import ArgumentParser

import crycript

# Set argument parser
parser = ArgumentParser(prog='crycript', description=f'Python symmetric encryption tool by SalvadorBG')

# Set version argument
parser.add_argument(
    '-v',
    '--version',
    help='show version and exit',
    action='version',
    version=crycript.STRING_VERSION
)

# Set same password argument
parser.add_argument(
    '-s',
    '--same-password',
    help='use the same password when dealing with multiple paths',
    action='store_true',
    dest='same_password'
)

# Set preserve argument
parser.add_argument(
    '-p',
    '--preserve',
    help='do not delete original files',
    action='store_true',
    dest='preserve'
)

# Set path argument
parser.add_argument(
    'path',
    help='path to file or directory',
    nargs='+'
)

# Set mutually exclusive arguments
parser_action_group = parser.add_mutually_exclusive_group(required=True)

# Set encryption action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-e',
    '--encrypt',
    help='encryption action',
    action='store_true'
)

# Set decryption action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-d',
    '--decrypt',
    help='decryption action',
    action='store_true'
)

# Set change password action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-c',
    '--change-password',
    help='change password action',
    action='store_true',
    dest='change_password'
)


if __name__ == '__main__':
    # Parse arguments
    arguments = parser.parse_args()

    # Set preserve
    crycript.constants.PRESERVE_ORIGINAL_FILES = arguments.preserve

    # Verify paths
    paths, filenames = crycript.path_validator(
        arguments.path, sort=False,
        action=(arguments.encrypt, arguments.decrypt, arguments.change_password)
    )

    key, old_key, new_key = None, None, None
    if arguments.same_password and len(paths) > 1:
        if arguments.encrypt:
            key = crycript.password_to_key()

        elif arguments.decrypt:
            key = crycript.password_to_key(confirm_password=False, generate_token=False)

        elif arguments.change_password:
            old_key = crycript.password_to_key(
                confirm_password=False, password_message='Old Password: ',
                generate_token=False)

            new_key = crycript.password_to_key(
                password_message='New Password: ',
                confirmation_message='Repeat Password: ',
                generate_token=True)

    for i, path in enumerate(paths):
        if len(paths) > 1:
            print(f'-> {filenames[i]}', end='\r') if arguments.same_password else print(f'-> {filenames[i]}')

        if arguments.encrypt:
            status = crycript.encrypt(path, key)
        elif arguments.decrypt:
            status = crycript.decrypt(path, key)
        elif arguments.change_password:
            status = crycript.change_password(path, old_key, new_key)
        print(status)
