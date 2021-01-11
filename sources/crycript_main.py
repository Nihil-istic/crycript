#!/usr/bin/env python

from argparse import ArgumentParser
from os.path import isfile, abspath

from crycript_functions_main import encrypt, decrypt, change_password
from crycript_functions_utility import bye, get_key
from crycript_globals import STR_VERSION
from crycript_interactive import Interactive
from cryptography.fernet import Fernet

# Set parser
parser = ArgumentParser(description='Python symmetric encryption tool by Salvador BG')

# Set version
parser.add_argument(
    '-v',
    '--version',
    help='show version and exit',
    action='version',
    version=STR_VERSION)

# Set interactive
parser.add_argument(
    '-i',
    '--interactive',
    help='launch interactive mode',
    action=Interactive)

# Set path argument
parser.add_argument(
    'path',
    help='path to file')

# Set mutually exclusive action (either encrypt or decrypt)
action = parser.add_mutually_exclusive_group()
action.add_argument(
    '-e',
    '--encrypt',
    help='encrypt a file',
    action='store_true')

action.add_argument(
    '-d',
    '--decrypt',
    help='decrypt a file',
    action='store_true')

action.add_argument(
    '-c',
    '--change-password',
    dest='change_password',
    help='change the password of an encrypted file',
    action='store_true')

# Parse arguments
args = parser.parse_args()

# Set absolute path
args_path = abspath(args.path)

# The script is designed to only work with files
if not isfile(args_path):
    bye('Path is not a file')

# Set preserve variable
PRESERVE = args.preserve

# Encrypt action
if args.encrypt:
    encryption_cipher = Fernet(get_key(True))
    status = encrypt(args_path, encryption_cipher)
    del encryption_cipher
    bye(status)

# Decrypt action
elif args.decrypt:
    decryption_cipher = Fernet(get_key(False))
    status = decrypt(args_path, decryption_cipher)
    del decryption_cipher
    bye(status)

# Change password action
elif args.change_password:
    status = change_password(args_path)
    bye(status)

# Action not selected
else:
    bye('You need to enter at least one action [-e | -d | -c]')
