#!/usr/bin/env python3.9

import argparse
import os

import crycript_functions
import crycript_globals

# Set argument parser
parser = argparse.ArgumentParser(description='Python symmetric encryption tool by SalvadorBG')

# Set version argument
parser.add_argument(
    '-v',
    '--version',
    help='show crycript version and exit',
    action='version',
    version=crycript_globals.STRING_VERSION
)

# Set source argument
parser.add_argument(
    '-s',
    '--source',
    help='show github source and exit',
    action='version',
    version='https://github.com/Nihil-istic/crycript'
)

# Set path argument
parser.add_argument(
    'path',
    help='path to file or directory',
)

# Set mutually exclusive arguments
parser_action_group = parser.add_mutually_exclusive_group()

# Set encryption action argument
parser_action_group.add_argument(
    '-e',
    '--encrypt',
    help='encrypt a file or directory',
    action='store_true',
)

# Set decryption action argument
parser_action_group.add_argument(
    '-d',
    '--decrypt',
    help='decrypt a file or directory',
    action='store_true',
)

# Set change password argument
parser_action_group.add_argument(
    '-c',
    '--change-password',
    help='change the password of an existing .cry file',
    action='store_true',
    dest='change_password'
)

# Parse arguments
arguments = parser.parse_args()

arguments = {
    'path': arguments.path,
    'encryption': arguments.encrypt,
    'decryption': arguments.decrypt,
    'change password': arguments.change_password
}

# Verify path
if not os.path.exists(arguments['path']):
    crycript_functions.kill('Aborted: path does not exist')

# Work with absolute path
arguments['path'] = os.path.abspath(arguments['path'])

if os.path.isdir(arguments['path']) or os.path.isfile(arguments['path']):

    if arguments['encryption']:
        status = crycript_functions.encrypt(arguments['path'])
        crycript_functions.kill(status)

    elif arguments['decryption']:
        status = crycript_functions.decrypt(arguments['path'])
        crycript_functions.kill(status)

    elif arguments['change password']:
        status = crycript_functions.change_password(arguments['path'])
        crycript_functions.kill(status)

    else:
        crycript_functions.kill('Aborted: you need to add one argument [-e | -d | -c]')

else:
    crycript_functions.kill('Aborted: path is not a file or directory')
