# This script changes the location from an
# "old location" (specified as a program argument with the -o flag) to a
# "new locaiton" (specified as a program argument with the -n flag) of the tracks in the
# rekordbox.xml file (filepath specified as a program argument with the -r flag) and saves it to a
# new location (out filepath specified as a program argument with the -p flag).


# system imports
from argparse import ArgumentParser
import logging
import os

# user imports
from rekordbox_client.RB_handler import RB_handler
from song_common.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def validate_paths(args) -> bool:
    if not args.path_to_rb or not os.path.isfile(args.path_to_rb):
        logger.error(
            "Location update was not started. Rekordbox XML file does not exist: %s",
            args.path_to_rb or "<not provided>",
        )
        return False

    if not args.save_location:
        logger.error(
            "Location update was not started. No output XML path was provided."
        )
        return False

    output_directory = os.path.dirname(args.save_location) or "."
    if not os.path.isdir(output_directory):
        logger.error(
            "Location update was not started. Output directory does not exist: %s",
            output_directory,
        )
        return False

    if args.old_location == "" or args.new_location == "":
        logger.error(
            "Location update was not started. Both old and new locations are required."
        )
        return False

    return True


def main(args) -> bool:
    if not validate_paths(args):
        return False

    logger.info("Start of program: change_location.py...")
    # instantiating the RB Handler and giving him the name benny ;)
    benny = RB_handler(args.path_to_rb)

    # changing the tracks location
    benny.change_tracks_source_path(
        old_location=args.old_location,
        new_location=args.new_location,
        location_of_interest=args.location_of_interest,
    )

    # saving the changed xml
    benny.export_data_to_xml(out_path=args.save_location)
    logger.info("End of program: change_location.py\n")
    return True


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--path-to-rb", default="")
    parser.add_argument("-o", "--old-location", default="")
    parser.add_argument("-n", "--new-location", default="")
    parser.add_argument("-p", "--save-location", default="")
    parser.add_argument("-l", "--location-of-interest", default="")

    args = parser.parse_args()
    if not main(args):
        raise SystemExit(1)
