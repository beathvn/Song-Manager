# This script creates a playlist of the new songs added to the playlists and new songs from favourite artists.


# system imports
from argparse import ArgumentParser
from datetime import datetime
import os

# 3rd party imports
import pandas as pd
import spotipy

# user imports
import helpers.dataloading as dataloading
import helpers.utils as utils


def create_playlist_playlists_new_arrivals(sp: spotipy.Spotify, config, playlist_name: str):
    df_playlists = pd.read_pickle(os.path.join(
        config['datapath'], 'playlists.pickle'))
    df_playlists_names = pd.read_pickle(os.path.join(
        config['datapath'], 'playlists_names.pickle'))
    df_popularity = pd.read_pickle(os.path.join(
        config['datapath'], 'popularity.pickle'))
    df_tracks = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks.pickle'))
    df_tracks_fav = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks_fav.pickle'))

    date_of_interest = df_playlists.sort_values(
        by=['date_added'], inplace=False, ascending=False).iloc[0].date_added

    # keeping just the newest adds to the playlists
    df_playlists = df_playlists[(df_playlists.date_removed.isnull()) & (
        df_playlists.date_added == date_of_interest)]

    # keeping just the playlists of interest (the dataset could hold also more playlists)
    df_playlists = df_playlists[df_playlists.id.isin(
        config['playlist_id_to_name'].keys())]

    # dropping tracks, that are already favourites
    df_playlists = df_playlists[~df_playlists.track_id.isin(df_tracks_fav.id)]

    # removing duplicates when looking at track_idid
    df_playlists.drop_duplicates(subset=['track_id'], inplace=True)

    # remove duplicated when looking at at track_name and artist
    df_playlists = df_playlists.join(
        df_tracks.set_index('id'), on='track_id', how='left')
    df_playlists.drop_duplicates(subset=['name', 'artists'], inplace=True)

    # getting the popularity info into it
    df_popularity = df_popularity[df_popularity.date == date_of_interest]
    df_popularity.drop(columns=['date'], inplace=True)
    df_playlists = df_playlists.join(
        df_popularity.set_index('id'), on='track_id', how='left')

    # getting the right amount of tracks per playlist (limited by config) - they must be sorted by popularity
    df_playlists.sort_values(by=['id', 'value'], inplace=True, ascending=False)

    # limiting the amount

    def filter(group, config):
        curr_playlist_id = group.head(1).id.iloc[0]
        current_limit = config['playlist_to_allowed_tracks'][curr_playlist_id]
        return group.head(current_limit)

    df_playlists = df_playlists.groupby(by='id', sort=False).apply(
        filter, config=config).reset_index(drop=True)

    len_before = len(df_playlists)
    df_playlists.dropna(subset=['track_id'], inplace=True)
    if len_before != len(df_playlists):
        print(
            f'Dropped {len_before - len(df_playlists)} rows due to missing track_id')

    # storing the created playlist
    df_playlists.rename(columns={
                        'id': 'playlist_id', 'value': 'popularity', 'name': 'track_name'}, inplace=True)
    df_playlists = df_playlists.join(
        df_playlists_names.set_index('id'), on='playlist_id', how='left')
    df_playlists.rename(columns={'name': 'playlist_name'}, inplace=True)
    df_playlists.to_pickle(os.path.join(
        config['datapath_playlists'], f'{date_of_interest} - from playlists.pickle'))

    # creating the playlist
    playlist_id = sp.user_playlist_create(
        user=config['username'], name=playlist_name, public=True)['id']
    # NOTE: possibly you can add a max of 100 tracks at once
    sp.playlist_add_items(playlist_id, df_playlists.track_id.tolist())


def create_playlist_artists_new_arrivals(sp: spotipy.Spotify, config: dict, playlist_name: str):
    df_artists_names = pd.read_pickle(os.path.join(
        config['datapath'], 'artists_names.pickle'))
    df_artists = pd.read_pickle(os.path.join(
        config['datapath'], 'artists.pickle'))
    df_tracks = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks.pickle'))
    df_tracks_fav = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks_fav.pickle'))

    date_of_interest = df_artists.sort_values(
        by=['date_added'], inplace=False, ascending=False).iloc[0].date_added

    # keeping just the newest adds to the artist
    df_artists = df_artists[(df_artists.date_removed.isnull()) & (
        df_artists.date_added == date_of_interest)]

    # keeping just the artists of interest (the dataset could hold also more artists)
    df_artists = df_artists[df_artists.id.isin(
        config['artist_id_to_name'].keys())]

    # dropping tracks, that are already favourites
    df_artists = df_artists[~df_artists.track_id.isin(df_tracks_fav.id)]

    # removing duplicates when looking at track_id
    df_artists.drop_duplicates(subset=['track_id'], inplace=True)

    # remove duplicated when looking at at track_name and artist
    df_artists = df_artists.join(
        df_tracks.set_index('id'), on='track_id', how='left')
    df_artists.drop_duplicates(subset=['name', 'artists'], inplace=True)

    len_before = len(df_artists)
    df_artists.dropna(subset=['track_id'], inplace=True)
    if len_before != len(df_artists):
        print(
            f'Dropped {len_before - len(df_artists)} rows due to missing track_id')

    # storing the created playlist
    df_artists.rename(columns={'id': 'artist_id',
                      'name': 'track_name'}, inplace=True)
    df_artists = df_artists.join(
        df_artists_names.set_index('id'), on='artist_id', how='left')
    df_artists.to_pickle(os.path.join(
        config['datapath_playlists'], f'{date_of_interest} - from artists.pickle'))

    # creating the playlist
    playlist_id = sp.user_playlist_create(
        user=config['username'], name=playlist_name, public=True)['id']
    # NOTE: possibly you can add a max of 100 tracks at once
    sp.playlist_add_items(playlist_id, df_artists.track_id.tolist())


def main(args):
    print('Start of program: create_new_songs_playlist.py...')
    ################## READING CONFIGURATION ##################
    config = dataloading.load_yaml(args.configfile)

    sp = utils.get_auth_spotipy_obj(config, scope='playlist-modify-public')

    create_playlist_playlists_new_arrivals(
        sp=sp,
        config=config,
        playlist_name='New Arrivals Playlists ' + datetime.now().strftime("%Y-%m-%d")
    )

    create_playlist_artists_new_arrivals(
        sp=sp,
        config=config,
        playlist_name='New Arrivals Artists ' + datetime.now().strftime("%Y-%m-%d")
    )

    print('End of program: create_new_songs_playlist.py\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--configfile')
    args = parser.parse_args()
    
    main(args)