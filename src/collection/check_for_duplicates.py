# This script checks for duplicates in your rekordbox xml file.
# Pass the path to your rekordbox.xml file as a program argument with the -p flag.


# system imports
from argparse import ArgumentParser
import logging

# user imports
import helpers.dataloading as dataloading
from helpers.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main(args):
    logger.info('Start of program: check_for_duplicates.py...')
    filepath = args.path_to_xml

    if filepath is None:
        raise ValueError(
            'Please provide a valid .xml filepath to your rekordbox database as a program argument!')

    data = dataloading.load_dataframe_from_rekordbox_xml(filepath)

    # searching for duplicates
    results = data['@Location'].duplicated()

    # printing the names of the duplicated songs
    duplicate_songnames = []
    for index, result in enumerate(results):
        if result:
            duplicate_songnames.append(data.iloc[index]['@Name'])

    if len(duplicate_songnames) != 0:
        logger.warning(
            f'🚨 {len(duplicate_songnames)} TRACKS WHERE FOUND pointing to the same file on your harddisk:')
        for currsong in duplicate_songnames:
            logger.warning('- ' + currsong)
    else:
        logger.info('✅ No songs appearing more than once were found.')
    
    logger.info('End of program: check_for_duplicates.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-p', '--path_to_xml')
    args = parser.parse_args()

    main(args)
