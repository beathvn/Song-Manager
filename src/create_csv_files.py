# Script to create csv files for liked tracks, tracks in specified playlists and tracks of selected artists.
# The script fetches the data from spotify


# system imports
from argparse import ArgumentParser
from datetime import datetime
import os

# user imports
import helpers.dataloading as dataloading
import helpers.datastoring as datastoring
from helpers.logger import logger
import helpers.utils as utils


def main(args):
    logger.info('Start of program: create_csv_files.py...')
    ################## READING CONFIGURATION ##################
    config = dataloading.load_yaml(args.configfile)
    username = config['username']
    data_path = config['datapath']
    
    sp = utils.get_auth_spotipy_obj(username)
    ################## END READING CONFIGURATION ##################
    
    # create csv of the current tracks in the playlists
    filename = datetime.now().strftime("%Y-%m-%d") + '-PLA.csv' # format: YYYY-MM-DD
    datastoring.create_csv_from_songs_in_playlists( sp=sp, 
                                                    username=username, 
                                                    outfile_name=os.path.join(data_path, filename),
                                                    playlists_of_interest=list(config['playlist_uri_to_name'].keys())
                                                    )
    
    # create csv of the current tracks the user liked
    filename = datetime.now().strftime("%Y-%m-%d") + '-FAV.csv'
    datastoring.create_fav_songs_csv(
        sp=sp,
        outfile_name= os.path.join(data_path, filename)
                                     )
    
    # create csv of the current top tracks of the artists the user follows
    filename = datetime.now().strftime("%Y-%m-%d") + '-ART.csv'
    datastoring.create_csv_from_songs_in_followed_artists(sp=sp,
                                                          outfile_name= os.path.join(data_path, filename),
                                                          artist_id_to_name=config['artist_id_to_name'],
                                                          )
    logger.info('End of program: create_csv_files.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--configfile')
    
    args = parser.parse_args()
    main(args)