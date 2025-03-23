# This script searches the difference of two xml files given as program arguments to the program.
# Make sure not to change the naming convention of the program, since it uses it to the the dateinformation
# the new_xml_file should be in this format: rekordbox6_YYYY-MM-DD.xml
# The changed files are outputted into the log file
# Newly added songs are ignored.


# system imports
from argparse import ArgumentParser
from datetime import datetime
import logging
import os
import sys
sys.path.append('../src/')

# 3rd party imports
import pandas as pd

# user imports
import helpers.dataloading as dataloading
from helpers.logging_config import setup_logging
import helpers.utils as utils

setup_logging()
logger = logging.getLogger(__name__)

def drop_by_columns(new_file: pd.DataFrame, old_file: pd.DataFrame, columns_to_reimport: list, columns_to_delete_and_reimport: list):
    df_reimport = pd.concat([new_file, old_file], axis=0).drop_duplicates(subset=columns_to_reimport, keep=False)
    df_delete_reimport = pd.concat([new_file, old_file], axis=0).drop_duplicates(subset=columns_to_delete_and_reimport, keep=False)

    # if we have a specific song, which was not dropped by the previous drop duplicates, we have a difference!
    # The song shows up twice, because it is present in new_file and old_file - we only want it once, to be able to print it out
    df_reimport.drop_duplicates(subset=['@Location'], keep='first', inplace=True)
    df_delete_reimport.drop_duplicates(subset=['@Location'], keep='first', inplace=True)

    df_reimport['action'] = 'REIMPORT'
    df_delete_reimport['action'] = 'DELETE & REIMPORT'

    df_changed = pd.concat([df_reimport, df_delete_reimport], axis=0).drop_duplicates(subset=['@Location'], keep='last')

    df_changed = df_changed.sort_values(by='action', inplace=False).reset_index(drop=True)

    logger.info(f'Found {len(df_changed)} differences (excluding the ones, that are simply new, or not in the specified location of interest')
    files_to_remove = []
    for _, row in df_changed.iterrows():
        if row['ComesFrom'] == 'old_file':
            files_to_remove.append(row)
        else:
            logger.info(f'Please {row["action"]} {row["@Name"]} - {row["@Artist"]}')
    
    logger.info(f"Found {len(files_to_remove)} files that should be missing within rekordbox:")
    for row in files_to_remove:
        logger.info(f'Please DELETE {row["@Name"]} - {row["@Artist"]}')


def main(args):
    logger.info('Start of program: diff_xml.py...')

    config = dataloading.load_yaml(args.config)
    datapath = config['datapath']

    new_file_path = os.path.join(datapath, config['new_xml_file'])
    old_file_path = os.path.join(datapath, config['old_xml_file'])
    logger.info(f"Calculating the difference between new_file: {new_file_path} and old_file: {old_file_path}")
    new_file = dataloading.load_dataframe_from_rekordbox_xml(new_file_path)
    old_file = dataloading.load_dataframe_from_rekordbox_xml(old_file_path)

    columns_to_consider = config['columns_to_consider'] + config['columns_to_consider_and_reimport']
    new_file = new_file[columns_to_consider]
    old_file = old_file[columns_to_consider]

    newest_date_to_keep = old_file.sort_values(by='@DateAdded', ascending=False)['@DateAdded'].iloc[0]
    len_before = len(new_file)
    new_file = new_file[new_file['@DateAdded'] <= newest_date_to_keep]
    if len_before != len(new_file):
        logger.warning(f'Dropped {len_before - len(new_file)} out of {len_before} rows of new file because they are newer than {newest_date_to_keep}')
        new_file.reset_index(drop=True, inplace=True)
    
    len_before = len(new_file)
    new_file = new_file[new_file['@Location'].str.startswith(config['location_to_consider'])]
    if len_before != len(new_file):
        logger.warning(f'Dropped {len_before - len(new_file)} out of {len_before} rows of new file because they were not in {config["location_to_consider"]}')
        new_file.reset_index(drop=True, inplace=True)
        assert len(new_file) != 0, logger.error(f'The provided location to consider: {config["location_to_consider"]} is not found once in new_file')

    assert len(old_file[old_file['@Location'].str.startswith(config['location_to_consider'])]) == len(old_file), logger.error(f'Found files with a different location than {config["location_to_consider"]} in old file')
    
    # i need those to understand afterwars where the rows come from
    new_file['ComesFrom'] = 'new_file'
    old_file['ComesFrom'] = 'old_file'

    drop_by_columns(new_file, old_file, config['columns_to_consider'], config['columns_to_consider_and_reimport'])

    # TODO: I don't want to calculate the filename again. Can't i get the logger handler somehow?
    if utils.query_yes_no('Open the log file?'):
        utils.open_file(f'./logs/log {datetime.now().strftime("%Y-%m-%d")}.txt')
    logger.info('End of program: diff_xml.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--config')

    args = parser.parse_args()
    main(args)