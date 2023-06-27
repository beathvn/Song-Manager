# This script searches the difference of two xml files given as program arguments to the program.
# Make sure not to change the naming convention of the program, since it uses it to the the dateinformation
# the new_xml_file should be in this format: rekordbox6_YYYY-MM-DD.xml
# The changed files are outputted into the log file
# Newly added songs are ignored.


# system imports
from argparse import ArgumentParser
from datetime import datetime
import os
import sys
sys.path.append('../src/')

# 3rd party imports
import pandas as pd

# user imports
import dataloading
from logger import logger
import utils


def main(args):    
    config = dataloading.load_yaml(args.config)
    datapath = config['datapath']

    files = [f for f in os.listdir(datapath) if os.path.isfile(os.path.join(datapath, f)) and not f.startswith('.') and f.startswith('rekordbox')]
    files.sort()
    new_filename = files[-1]
    new_file = dataloading.load_dataframe_from_rekordbox_xml(os.path.join(datapath, new_filename))
    old_file = dataloading.load_dataframe_from_rekordbox_xml(os.path.join(datapath, config['old_xml_file']))

    logger.info(f'As newest xml file, i am using the following file: {new_filename}')

    columns_to_consider = config['columns_to_consider']
    new_file = new_file[columns_to_consider]
    old_file = old_file[columns_to_consider]

    df_changed = pd.concat([new_file, old_file], axis=0).drop_duplicates(keep=False)
    df_changed = df_changed[df_changed['@DateAdded'] != new_filename[11:-4]]
    df_changed = df_changed[df_changed['@Location'].str.startswith(config['location_to_consider'])]
    df_changed.drop_duplicates(subset=['@Location'], keep='first', inplace=True)
    df_changed = df_changed.sort_values(by='@Name', inplace=False).reset_index(drop=True)
    df_changed
    logger.info(f'Found {len(df_changed)} changes (excluding the ones, that are simply new, or not in Music Collection)')

    # now write the files to a file using the logger
    for _, row in df_changed.iterrows():
        logger.info(f'Please reimport {row["@Name"]} - {row["@Artist"]}')

    # TODO: I don't want to calculate the filename again. Can't i get the logger handler somehow?
    if utils.query_yes_no('Open the log file?'):
        utils.open_file(f'./logs/log {datetime.now().strftime("%Y-%m-%d")}.txt')


if __name__ == "__main__":
    logger.info('Start of program: Diff XML')

    parser = ArgumentParser()
    parser.add_argument('-c', '--config')

    args = parser.parse_args()
    main(args)
    
    logger.info('End of program: Diff XML\n')