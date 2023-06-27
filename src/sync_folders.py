# This script syncs folders given as arguments using rsync.
# Updating a Versions.txt file with a row containing "Music Collection" Key word


# system imports
from argparse import ArgumentParser
import os
import unicodedata
import subprocess
from datetime import datetime

# 3rd party imports
from colorama import Fore, Style

# user imports
from logger import logger


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


def sync_folders(master_folder: str, slave_folder: str, logger):
    """
    Synchronize folders from the master folder to the slave folder using rsync.

    Args:
        master_folder (str): Path to the master folder.
        slave_folder (str): Path to the slave folder.
        logger: Logger object used for logging information.

    Returns:
        None
    """
    print(f"Syncing folders from {master_folder} to {slave_folder}")
    logger.info(f"Syncing folders from {master_folder} to {slave_folder}")

    # ---------------------------- check for illegal characters ----------------------------
    # Check if the master folder holds any characters causing problems when syncing

    print(f'Checking for illegal characters in {master_folder}')
    logger.info(f'Checking for illegal characters in {master_folder}')

    files = [f for f in os.listdir(master_folder) if os.path.isfile(
        os.path.join(master_folder, f)) and not f.startswith('.')]

    illegal_files = []

    for file in files:
        if contains_illegal_characters(file):
            illegal_files.append(file)
    if len(illegal_files) != 0:
        print(
            Fore.RED + f'Found illegal characters in {master_folder}! ABORTING!' + Style.RESET_ALL)
        logger.error(f'Found illegal characters in {master_folder}! ABORTING!')
        raise ValueError(
            'Master folder contains files with illegal characters: ' + str(illegal_files))
    else:
        print(Fore.GREEN +
              f'No illegal characters found in {master_folder}. Continuing' + Style.RESET_ALL)
        logger.info(
            f'No illegal characters found in {master_folder}. Continuing...')

    # ---------------------------- sync folders ----------------------------
    command = ["rsync", "-av", "--delete",
               "--stats", master_folder + "/", slave_folder, "--exclude", ".*"]

    output = subprocess.check_output(command, universal_newlines=True)

    # Extract copied file count
    copied_files_cnt = int(output.split(
        "Number of files transferred: ")[1].split()[0])

    if copied_files_cnt > 0:
        print("Copied files: " + Fore.GREEN
              + f"{copied_files_cnt}" + Style.RESET_ALL)
        logger.info(f"Copied files: {copied_files_cnt}")

        copied_files = output.split(
            './')[1].split('\n', copied_files_cnt+1)[1:-1]

        for file in copied_files:
            print(f"Copied file:\t\t " + Fore.GREEN +
                  f"{file:<30}" + Style.RESET_ALL)
            logger.info(f"Copied file:\t\t {file:<30}")
    else:
        logger.info("No files copied!")
        print("No files copied!")

    # Extract deleted file list
    deleted_files = [
        line.split(None, 1)[-1].strip() for line in output.splitlines() if line.startswith("deleting")
    ]

    if len(deleted_files) > 0:
        print(f"Deleted files: " + Fore.RED +
              f"{len(deleted_files)}" + Style.RESET_ALL)
        logger.warning(f"Deleted files: {len(deleted_files)}")
        for file in deleted_files:
            print(f"Deleted file:\t\t " + Fore.RED +
                  f"{file:<30}" + Style.RESET_ALL)
            logger.warning(f"Deleted file:\t\t {file:<30}")
    else:
        logger.info("No files deleted!")
        print("No files deleted!")

    print("Sync completed!")
    logger.info("Sync completed!")
    return


def main(args):
    sync_folders(master_folder=args.master_folder,
                 slave_folder=args.slave_folder,
                 logger=logger,
                 )

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
