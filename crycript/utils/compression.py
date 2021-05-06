from os import walk, remove, rmdir
from os.path import join as os_join, basename
from tarfile import open as tar_open

from .. import constants


def delete_directory(dir_to_delete: str):
    """Remove all the contents of a given directory, then remove it.

    dir_to_delete: str -> path to directory to delete"""
    # Loop on the contents of a directory from down to top
    for root, dirs, files in walk(dir_to_delete, topdown=False):

        # Loop on files
        for name in files:
            # Remove file
            remove(os_join(root, name))

        # Loop on directories
        for name in dirs:
            # Remove (empty) directory
            rmdir(os_join(root, name))

    # Remove (now empty) directory
    rmdir(dir_to_delete)


def path_to_tar_gz(input_path: str, output_path: str):
    """Create a tar gz file based on the given directory, then remove the original directory.

    input_path: str -> path to compress
    output_path: str -> path to new tar gz file"""
    # Open a new tar gz file
    with tar_open(output_path, 'w:gz') as tar:
        # Add the contents of the directory to new tar gz file
        tar.add(input_path, arcname=basename(input_path))

    # Remove directory (now compressed as tar gz file)
    if not constants.PRESERVE_ORIGINAL_FILES:
        delete_directory(input_path)


def tar_gz_to_directory(input_tar_gz: str, output_directory: str):
    """Extract the given tar gz file in the given parent directory.

    input_tar_gz: str -> path to tar gz file to decompress
    output_directory: str -> path to parent directory for the extracted contents"""
    # Open the tar gz file
    with tar_open(input_tar_gz, 'r:gz') as tar:
        # Extract all its contents
        tar.extractall(members=tar.getmembers(), path=output_directory)

    # Remove tar gz file
    remove(input_tar_gz)
