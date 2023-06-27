# Script to create csv files for liked tracks, tracks in specified playlists and tracks of selected artists.
# The script fetches the data from spotify


# system imports
from argparse import ArgumentParser
from datetime import datetime
import os

# 3rd party imports
import spotipy
import spotipy.util as util

# user imports
import dataloading
import datastoring


def main(args):
    ################## READING CONFIGURATION ##################
    config = dataloading.load_yaml(args.configfile)
    username = config['username']
    data_path = config['datapath']
    
    # getting the environmental variables
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
    
    if client_id is None:
        raise Exception('SPOTIPY_CLIENT_ID environmental variable not found')
    elif client_secret is None:
        raise Exception('SPOTIPY_CLIENT_SECRET environmental variable not found')
    elif redirect_uri is None:
        raise Exception('SPOTIPY_REDIRECT_URI environmental variable not found')

    token = util.prompt_for_user_token(
            username=username,
            scope='playlist-modify-public',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=token)

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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--configfile')
    
    args = parser.parse_args()
    main(args)