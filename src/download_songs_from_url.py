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


def main(args):
    config = dataloading.load_yaml(args.config)

    # getting the environmental variables
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

    if client_id is None:
        raise Exception('SPOTIPY_CLIENT_ID environmental variable not found')
    elif client_secret is None:
        raise Exception('SPOTIPY_CLIENT_SECRET environmental variable not found')

    # setting up the spotipy object
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    songs = dataloading.get_txt_lines_as_list(config['urllist'])

    # adding the spotify uris
    playlist_tracks = sp.user_playlist_tracks(
        config['username'], playlist_id=config['playlist'])['items']

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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--config')

    args = parser.parse_args()
    main(args)
