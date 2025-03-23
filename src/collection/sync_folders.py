# This script syncs folders given as arguments using rsync.
# Updating a Versions.txt file with a row containing "Music Collection" Key word


# system imports
from argparse import ArgumentParser
from datetime import datetime
import logging
import os
import sys

sys.path.append("./src")

# 3rd party imports
from dirsync import sync

# user imports
from helpers.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


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
    with open(version_file, "rt") as file:
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
            f'Folder name "{folder_name}" not found in text file. Check spelling!'
        )
    else:
        logger.info(f'Updated "{folder_name}" to "{current_date}"')

    # Write the modified list back to the text file
    with open(version_file, "wt") as file:
        file.writelines(lines)


def sync_folders(master_folder: str, slave_folder: str):
    sync(
        master_folder,
        slave_folder,
        "sync",
        verbose=True,
        ignore=["\."],
        logger=logger,
        purge=True,
    )


def main(args):
    logger.info("Start of program: sync_folders.py...")
    sync_folders(args.master_folder, args.slave_folder)

    if args.master_folder.endswith("Music Collection"):
        update_versions_txt(
            version_file=os.path.join(
                os.path.dirname(args.slave_folder), "Versions.txt"
            ),
            folder_name="Music Collection",
        )
    else:
        logger.warning(
            'Syncing folder is not "Music Collection". Not updating Versions.txt'
        )
    logger.info("End of program: sync_folders.py\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--master_folder")
    parser.add_argument("-s", "--slave_folder")

    args = parser.parse_args()
    main(args)
