# This script creates a playlist of the new songs added to the playlists and new songs from favourite artists.


# system imports
from argparse import ArgumentParser
from datetime import datetime
import os

# 3rd party imports
import pandas as pd
import spotipy
import spotipy.util as util

# user imports
import dataloading
import dataprocessing
from logger import logger


def get_new_arrival_song_list_and_limit(data_path: str, dict_playlist_limits: dict, dict_uri_to_name: dict)-> list:
    """Finds the new songs, added from the last time the csv got saved to today. 
    Adds just as many tracks allowed by dict_playlist_limits. 
    
    Songs already saved are ignored and the most popular songs are added.

    Args:
        data_path (str): path where the csv files are stored (they should be in a YYYY-MM-DD.csv form)
        dict_playlist_limits (dict): keys are the playlist ids and value is the allowed tracks to be added
        dict_uri_to_name (dict): keys are the playlist uris and value is the actual name of the playlist

    Returns:
        list: lists the uri of the unique songs
    """

    df_pla_old, df_pla_new, df_art_old, df_art_new, df_fav = dataloading.get_dataframes_from_folder(data_path)

    pla_new = dataprocessing.filter_df_new_arrivals(df_old=df_pla_old, df_new=df_pla_new)
    art_new = dataprocessing.filter_df_new_arrivals(df_old=df_art_old, df_new=df_art_new)

    # combining the dataframes
    df_new_arrivals = pd.concat([pla_new, art_new], ignore_index=True)

    added_by_artist = art_new.value_counts(subset=['artist_name'])
    for index, value in enumerate(added_by_artist):
        logger.info(f'added {value} new tracks from the artist {added_by_artist.index[index][0]}')

    # dropping the already saved tracks
    df_new_arrivals = dataprocessing.remove_saved_tracks_from_df(df=df_new_arrivals, saved_track_ids=set(df_fav['id']))


    # limiting the dataframe (with amount, popularity):
    df_thin = dataprocessing.limit_df_count(df=df_new_arrivals, dict_playlist_limits=dict_playlist_limits, dict_uri_to_name=dict_uri_to_name)

    return df_thin['track_id'].to_list()


def create_playlist_of_songlist(sp: spotipy.Spotify, username: str, playlist_name: str, song_list: list)-> None:
    """Creates a spotify playlist with the provided songs

    Args:
        sp (spotipy.Spotify): configured spotify object, which talks to the Spotify Web API
        username (str): username of the person you want to create the playlist for
        playlist_name (str): name of the playlist
        song_list (list): uri list of the songs you want to add to the playlist
    """
    # creating the playlist
    playlist_id = sp.user_playlist_create(user=username, name=playlist_name, public=True)['id']

    # you can just add 100 tracks at a time
    max_len = 100
    if len(song_list) > max_len:
        for i in range((len(song_list) + max_len - 1) // max_len):
            sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=song_list[i*max_len:(i+1)*max_len])
    else:
        sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=song_list)

    return


def main(args):
    ################## READING CONFIGURATION ##################
    config = dataloading.load_yaml(args.configfile)
    username = config['username']
    data_path = config['datapath']
    
    # getting the environmental variables
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
    
    # check if they are set
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
    
    dict_playlist_limits = config['playlist_to_allowed_tracks']
    
    # secondly, find all the unique songs from the last two files
    song_list = get_new_arrival_song_list_and_limit(data_path=data_path, dict_playlist_limits=dict_playlist_limits, dict_uri_to_name=config['playlist_uri_to_name'])

    # thirdly, create the playlist with the songs
    playlist_name = config['playlist_name'] + ' ' + datetime.now().strftime("%Y-%m-%d")
    create_playlist_of_songlist(sp=sp,
                                username=username,
                                playlist_name=playlist_name,
                                song_list=song_list,
                                )
    logger.info(f'Created the playlist {playlist_name} with {len(song_list)} songs for the user {username} songs!')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--configfile')
    args = parser.parse_args()
    
    main(args)