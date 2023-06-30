# This script syncs folders given as arguments using rsync.
# Updating a Versions.txt file with a row containing "Music Collection" Key word


# system imports
from argparse import ArgumentParser
import os
import unicodedata
import subprocess
from datetime import datetime

# 3rd party imports
from dirsync import sync
from colorama import Fore, Style

# user imports
from helpers.logger import logger


def update_versions_txt(version_file: str, folder_name: str) -> None:
    """
    Update the version information for a folder in a text file.

    Args:
        version_file (str): The path to the text file containing version information.
        folder_name (str): The name of the folder to update.

    Raises:
        ValueError: If the folder name is not found in the text file.

    Returns:
        None
    """

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Read the contents of the text file into a list
    with open(version_file, 'rt') as file:
        lines = file.readlines()

    did_change = False

    # Find the line to update
    for i, line in enumerate(lines):
        if line.startswith(folder_name):
            # Update the line with the new date
            lines[i] = f"{folder_name}\t{current_date}\n"
            did_change = True
            break

    if not did_change:
        raise ValueError(
            f'Folder name "{folder_name}" not found in text file. Check spelling!')
    else:
        print(Fore.GREEN +
              f'Updated "{folder_name}" to "{current_date}"' + Style.RESET_ALL)

    # Write the modified list back to the text file
    with open(version_file, 'wt') as file:
        file.writelines(lines)


def contains_illegal_characters(text):
    """
    checking for illegal characters according to unicodedata
    """
    result = False
    for char in text:
        if unicodedata.combining(char) != 0:
            result = True
    return result


def sync_folders(master_folder: str, slave_folder: str):
    filenames_to_exclude = [filename for filename in os.listdir(master_folder) if filename.startswith('.')]
    sync(master_folder, slave_folder, 'sync', verbose=True, exclude=filenames_to_exclude, logger=logger, purge=True)


def main(args):    
    sync_folders(args.master_folder, args.slave_folder)

    if args.master_folder.endswith('Music Collection'):
        update_versions_txt(version_file=os.path.join(
            os.path.dirname(args.slave_folder), 'Versions.txt'), folder_name='Music Collection')
    else:
        print('Syncing folder is not "Music Collection". Not updating Versions.txt')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-m', '--master_folder')
    parser.add_argument('-s', '--slave_folder')

    args = parser.parse_args()
    main(args)
