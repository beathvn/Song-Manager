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
import helpers.dataloading as dataloading
from helpers.logger import logger
import helpers.utils as utils


def main(args):
    logger.info('Start of program: diff_xml.py...')

    config = dataloading.load_yaml(args.config)
    datapath = config['datapath']

    new_file_path = os.path.join(datapath, config['new_xml_file'])
    old_file_path = os.path.join(datapath, config['old_xml_file'])
    logger.info(f"Calculating the difference between new_file: {new_file_path} and old_file: {old_file_path}")
    new_file = dataloading.load_dataframe_from_rekordbox_xml(new_file_path)
    old_file = dataloading.load_dataframe_from_rekordbox_xml(old_file_path)

    columns_to_consider = config['columns_to_consider']
    new_file = new_file[columns_to_consider]
    old_file = old_file[columns_to_consider]

    newest_date_to_keep = old_file.sort_values(by='@DateAdded', ascending=False)['@DateAdded'].iloc[0]
    len_before = len(new_file)
    new_file = new_file[new_file['@DateAdded'] <= newest_date_to_keep]
    logger.warning(f'Dropped {len_before - len(new_file)} out of {len_before} rows of new file because they are newer than {newest_date_to_keep}')
    
    len_before = len(new_file)
    new_file = new_file[new_file['@Location'].str.startswith(config['location_to_consider'])]
    logger.warning(f'Dropped {len_before - len(new_file)} rows of new file because they were not in {config["location_to_consider"]}')

    len_before = len(old_file)
    old_file = old_file[old_file['@Location'].str.startswith(config['location_to_consider'])]
    if len(old_file) != len_before:
        logger.error('Dropped something that should not have been dropped')
        raise ValueError('Dropped something that should not have been dropped')
    
    # i need those to understand afterwars where the rows come from
    new_file['ComesFrom'] = 'new_file'
    old_file['ComesFrom'] = 'old_file'

    df_changed = pd.concat([new_file, old_file], axis=0).drop_duplicates(subset=columns_to_consider, keep=False)

    # if we have a specific song, which was not drop by the previous drop duplicates, we have a difference
    # but the song shows up twice, because it is present in new_file and old_file
    df_changed.drop_duplicates(subset=['@Location'], keep='first', inplace=True)

    df_changed = df_changed.sort_values(by='@Name', inplace=False).reset_index(drop=True)

    logger.info(f'Found {len(df_changed)} differences (excluding the ones, that are simply new, or not in Music Collection)')
    files_to_remove = []
    for _, row in df_changed.iterrows():
        if row['ComesFrom'] == 'old_file':
            files_to_remove.append(row)
        else:
            logger.info(f'Please DELETE & REIMPORT {row["@Name"]} - {row["@Artist"]}')
    
    logger.info(f"Found {len(files_to_remove)} files that should be missing within rekordbox:")
    for row in files_to_remove:
        logger.info(f'Please DELETE {row["@Name"]} - {row["@Artist"]}')

    # TODO: I don't want to calculate the filename again. Can't i get the logger handler somehow?
    if utils.query_yes_no('Open the log file?'):
        utils.open_file(f'./logs/log {datetime.now().strftime("%Y-%m-%d")}.txt')
    logger.info('End of program: diff_xml.py\n')


if __name__ == "__main__":
    logger.info('Start of program: Diff XML')

    parser = ArgumentParser()
    parser.add_argument('-c', '--config')

    args = parser.parse_args()
    main(args)
    
    logger.info('End of program: Diff XML\n')