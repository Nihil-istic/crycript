#!/usr/bin/env python3.9

from argparse import ArgumentParser
from os.path import isfile, isdir, abspath, exists

import CrycriptFunctions
import CrycriptGlobals

# Set argument parser
parser = ArgumentParser(description='Python symmetric encryption tool by SalvadorBG')

# Set version argument
parser.add_argument(
    '-v',
    '--version',
    help='show crycript version and exit',
    action='version',
    version=CrycriptGlobals.STRING_VERSION
)

# Set path argument
parser.add_argument(
    'path',
    help='path to file or directory',
)

# Set mutually exclusive arguments
parser_action_group = parser.add_mutually_exclusive_group()

# Set encryption action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-e',
    '--encrypt',
    help='encrypt a file or directory',
    action='store_true',
)

# Set decryption action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-d',
    '--decrypt',
    help='decrypt a file or directory',
    action='store_true',
)

# Set change password action (inside mutually exclusive group)
parser_action_group.add_argument(
    '-c',
    '--change-password',
    help='change the password of an existing crycript file',
    action='store_true',
    dest='change_password'
)

# Parse arguments
arguments = parser.parse_args()

# Make sure path exists
if not exists(arguments.path):
    CrycriptFunctions.kill('Aborted: path does not exist')

# Make sure path is absolute
arguments.path = abspath(arguments.path)

# Crycript only works with files and directories
if isdir(arguments.path) or isfile(arguments.path):

    # Encryption
    if arguments.encrypt:
        status = CrycriptFunctions.encrypt(arguments.path)
        CrycriptFunctions.kill(status)

    # Decryption
    elif arguments.decrypt:
        status = CrycriptFunctions.decrypt(arguments.path)
        CrycriptFunctions.kill(status)

    # Change password
    elif arguments.change_password:
        status = CrycriptFunctions.change_password(arguments.path)
        CrycriptFunctions.kill(status)

    # No default action
    else:
        CrycriptFunctions.kill('Aborted: you must set one argument: [-e | -d | -c]')

else:
    CrycriptFunctions.kill('Aborted: path is not a file or directory')
