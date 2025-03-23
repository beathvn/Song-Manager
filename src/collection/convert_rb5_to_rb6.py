# This script updates a rekordbox 6 xml file according to a rekordbox 5 xml file.
# The keys, that are updated are specified in the keys_to_update list.


# system imports
from argparse import ArgumentParser
import logging

# user imports
from helpers.RB_handler import RB_handler_five_six
from helpers.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main(args):
    logger.info('Start of program: convert_rb5_to_rb6.py...')
    # define here the keys you want to update
    keys_to_update = ['@Name', '@Artist', '@Album', '@Genre',
                      '@Rating', 'POSITION_MARK', '@Comments', '@PlayCount', '@Grouping', '@Colour']

    # instantiating the RB Handler and giving him the name mark ;)
    mark = RB_handler_five_six(args.path_to_rb5, args.path_to_rb6,
                               args.loc_of_musicfiles, keys_to_update)

    # updating rekordbox 6 according to 5
    mark.update_rb6_according_to_5()

    # writing the log message. This holds information about what tracks were updated, which were skipped and so on
    mark.write_log_message()

    # exporting the changed data into an xml, so that we can import it later into rekordbox
    mark.export_data_to_xml(args.output_file)
    logger.info('End of program: convert_rb5_to_rb6.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument('-5', '--path_to_rb5', default='')
    parser.add_argument('-6', '--path_to_rb6', default='')
    parser.add_argument('-l', '--loc_of_musicfiles', default='')
    parser.add_argument('-o', '--output_file', default='output.xml')
    
    args = parser.parse_args()

    main(args)
