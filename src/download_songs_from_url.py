# This script downloads the songs provided in a file url text file 
# (filepath specified as a program argument with the -l flag) using ytmdl
# The urlfile should contain one url per line and they should be in the same order 
# as the playlist provided in the -p flag.
# The provided playlist should be a playlist of the user provided in the -u flag.


# system imports
from argparse import ArgumentParser
import os

# 3rd party imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# user imports
import helpers.dataloading as dataloading
import helpers.dataprocessing as dataprocessing
from helpers.logger import logger
import helpers.utils as utils


def main(args):
    logger.info('Start of program: download_songs_from_url.py...')
    config = dataloading.load_yaml(args.config)
    connection = dataloading.load_yaml(args.connection)
    username = connection['username']

    sp = utils.get_auth_spotipy_obj(connection, 'playlist-modify-public')

    songs = dataloading.get_txt_lines_as_list(config['urllist'])

    # adding the spotify uris
    playlist_tracks = sp.user_playlist_tracks(
        username, playlist_id=config['playlist'])['items']

    songs = [x + ' --spotify-id ' + y['track']['uri']
             for x, y in zip(songs, playlist_tracks)]

    # disable local search
    songs = [i + ' --nolocal' for i in songs]

    # we can use fast search, since we selected the urls already
    songs = [i + ' -q' for i in songs]

    songs = dataprocessing.adding_pre_and_post_str(
        'ytmdl', '--output-dir ' + config['output_dir'], songs)

    # passing the commands to the command line
    for song in songs:
        os.system(song)
    logger.info('End of program: download_songs_from_url.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-n', '--connection',
                        default='./config/connection.yaml')
    parser.add_argument('-c', '--config',
                        default='./config/download.yaml')

    args = parser.parse_args()
    main(args)
