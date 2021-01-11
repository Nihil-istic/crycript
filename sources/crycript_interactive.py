from argparse import Action
from os import listdir
from os.path import isfile, isdir, expanduser, dirname, abspath

from crycript_functions_main import encrypt, decrypt, change_password, get_key
from crycript_functions_utility import bye
from crycript_globals import MENU_WIDTH, STR_VERSION
from cryptography.fernet import Fernet


def global_menu():
    try:
        # Create interactive menu
        menu = [
            f' {STR_VERSION} '.center(MENU_WIDTH, '-') + '\n',
            '-' + '1) encrypt a file'.center(MENU_WIDTH - 2, ' ') + '-' + '\n',
            '-' + '2) decrypt a file'.center(MENU_WIDTH - 2, ' ') + '-' + '\n',
            '-' + '3) change a password'.center(MENU_WIDTH - 2, ' ') + '-' + '\n',
            '-' + '4) exit'.center(MENU_WIDTH - 2, ' ') + '-' + '\n',
            ''.center(MENU_WIDTH, '-') + '\n'
        ]

        # Print to screen
        print(''.join(menu))

        # Get a input
        while True:
            try:
                option = int(input('> ').strip())
                if 0 < option <= len(menu) - 2:
                    return option
                else:
                    print(f'You can only enter a number between 1 and {len(menu) - 2}, try again')
                    continue
            except ValueError:
                print('You can only enter integer values, try again')
                continue

    # Exit when ctrl + c is pressed
    except KeyboardInterrupt:
        bye()

    # Exit when ctrl + d is pressed
    except EOFError:
        bye()


def path_browser(initial_path=expanduser('~')):
    try:
        current_path = abspath(initial_path)

        current_path_elements = listdir(current_path)
        current_path_elements.sort()

        current_path_files, current_path_dirs = [], []

        for element in current_path_elements:
            root_element = current_path + '/' + element

            if element.startswith('.'):
                continue

            elif isfile(root_element):
                current_path_files.append(element)

            elif isdir(root_element):
                current_path_dirs.append(element)

        current_path_elements = current_path_dirs + current_path_files

        current_path_to_print = '[' + current_path.center(MENU_WIDTH - 2, ' ') + ']'

        if len(current_path_to_print) > MENU_WIDTH:
            current_path_to_print = '[' + ('...'
                                           + current_path[len(current_path)
                                                          - MENU_WIDTH + 2 + 3:]).center(MENU_WIDTH - 2, ' ') + ']'

        print('\n' + current_path_to_print)

        dirs_to_print, files_to_print = ['[' + 'Directories'.center(MENU_WIDTH//2 - 2, ' ') + ']'], \
                                        ['[' + 'Files'.center(MENU_WIDTH//2 - 2, ' ') + ']']

        last_dir_n = -1

        for n, element in enumerate(current_path_dirs):
            last_dir_n = n
            dirs_to_print.append(f'[{n}] {element}')

        first_file_n = 0 if last_dir_n == -1 else last_dir_n + 1

        for n, element in enumerate(current_path_files):
            files_to_print.append(f'[{n + first_file_n}] {element}')

        while len(dirs_to_print) != len(files_to_print):
            if len(dirs_to_print) < len(files_to_print):
                dirs_to_print.append('---')
            else:
                files_to_print.append('---')

        if len(dirs_to_print) == 1:
            dirs_to_print.append('---')
            files_to_print.append('---')

        to_print = [[dirs_to_print[i], files_to_print[i]] for i in range(len(dirs_to_print))]

        for dir_line, file_line in to_print:
            if len(dir_line) > MENU_WIDTH//2:
                dir_line = dir_line[:-1 * (len(dir_line) - MENU_WIDTH//2 + 4)] + '... '

            if len(file_line) > MENU_WIDTH//2:
                file_line = file_line[:-1 * (len(file_line) - MENU_WIDTH//2 + 4)] + '... '

            print(f"{dir_line + ''.join([' ' for _ in range(MENU_WIDTH//2 - len(dir_line))])}"
                  f"{file_line + ''.join([' ' for _ in range(MENU_WIDTH//2 - len(file_line))])}")

        print('Enter [b] to go back one directory')

        while True:
            option = input('> ').strip().lower()
            if option == 'b':
                return path_browser(dirname(current_path))
            else:
                try:
                    option = int(option)
                except ValueError:
                    print('Please enter numeric value')
                    continue

                if option < 0 or option > len(current_path_elements) - 1:
                    print('Please enter a valid number')

                elif option < first_file_n:
                    return path_browser(current_path + '/' + current_path_dirs[option])

                else:
                    return current_path + '/' + current_path_files[option - first_file_n]

    # Exit when ctrl + c is pressed
    except KeyboardInterrupt:
        bye()

    # Exit when ctrl + d is pressed
    except EOFError:
        bye()


def pager(n):
    if n == 4:  # Exit
        bye()
    else:
        path = path_browser()

    if n == 1:  # Encrypt
        encryption_cipher = Fernet(get_key(True))
        status = encrypt(path, encryption_cipher)
        del encryption_cipher
        bye(status)

    elif n == 2:  # Decrypt
        decryption_cipher = Fernet(get_key(False))
        status = decrypt(path, decryption_cipher)
        del decryption_cipher
        bye(status)

    elif n == 3:  # Change password
        status = change_password(path)
        bye(status)


def main():
    option = global_menu()
    pager(option)


class Interactive(Action):
    def __init__(self, nargs=0, **kw):
        if nargs != 0:
            raise ValueError("nargs not allowed")
        super(Interactive, self).__init__(nargs=nargs, **kw)

    def __call__(self, parser, namespace, values, option_string=None):
        main()
