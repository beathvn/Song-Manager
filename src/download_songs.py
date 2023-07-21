# This script downloads the songs from a specified playlists
# (given as a program argument with the -p flag) using ytmdl.
# The playlist must be a playlist of the user provided in the -u flag.
# On each song the user is asked, which song he wants to download
# The output directory is specified with the -o flag.


# system imports
import os
from argparse import ArgumentParser

# 3rd party imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# user imports
import helpers.dataprocessing as dataprocessing
import helpers.dataloading as dataloading
from helpers.logger import logger
import helpers.utils as utils


def list_songs_from_spotify_playlist(sp, user, playlist):

    playlist_tracks = sp.user_playlist_tracks(
        user, playlist, fields='items,uri,name,id', market='fr')

    playlist_tracks = playlist_tracks['items']
    str_playlist = []

    for track in playlist_tracks:
        track = track['track']
        artists = [i['name'] for i in track['artists']]
        str_playlist.append(
            track['name'] + ' ' + ' '.join(artists) + ' --spotify-id ' + track['uri'])
    return str_playlist


def main(args):
    logger.info('Start of program: download_songs.py...')
    config = dataloading.load_yaml(args.config)
    username = config['username']

    sp = utils.get_auth_spotipy_obj(username)

    # since the ytmdl is just a command line tool, we need to call it in the shell
    songs = list_songs_from_spotify_playlist(sp=sp,
                                      playlist=config['playlist'], user=config['username'])
    
    songs = dataprocessing.remove_illegal_characters(songs)

    # disable local search
    songs = [i + ' --nolocal' for i in songs]

    songs = dataprocessing.adding_pre_and_post_str(
        'ytmdl', '--output-dir ' + config['output_dir'], songs)

    for song in songs:
        os.system(song)
    logger.info('End of program: download_songs.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    main(args)
