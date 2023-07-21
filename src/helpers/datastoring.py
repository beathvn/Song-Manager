# This script provides different functions to save .csv files from spotify.


# system imports
import math
import os

# 3rd party imports
import pandas as pd
import spotipy
from tqdm import tqdm

# user imports
import helpers.dataloading as dataloading
from logger import logger


def create_fav_songs_csv(sp: spotipy.Spotify, outfile_name: str)-> None:
    """Creates a csv file holding all the Liked tracks of the user with which the spotify object is configured

    Args:
        sp (spotipy.Spotify): configured spotify object, which talks to the Spotify Web API
        outfile_name (str): filename (with whole filepath), with which the outfile will get stored. Make sure to include also .csv at the end
    """

    if os.path.exists(outfile_name):
        logger.warn('csv file already exists')
        return

    # getting all saved tracks:
    # Set up an empty list to store the results
    results = []

    # Loop through the results until we have retrieved all tracks
    total_tracks = sp.current_user_saved_tracks(limit=1, offset=0)['total']
    iterations = math.ceil(total_tracks / 50)       # 50 is the max amount you can fetch in a single request

    for curr_iteration in tqdm(range(iterations), desc='Creating favourite songs csv', unit='packs of 50 songs'):
        track_results = sp.current_user_saved_tracks(limit=50, offset=curr_iteration * 50)

        # Add the retrieved tracks to our results list
        results += track_results['items']
        

    logger.info(f"Retrieved {len(results)} saved tracks.")

    # formatting and filtering the data and saving it
    df_messy = pd.DataFrame(results)

    # Use json_normalize to expand the dict into separate columns
    df_expanded = pd.json_normalize(df_messy['track'])

    # Concatenate the expanded columns with the original dataframe, dropping the 'track' column
    df = pd.concat([df_messy.drop('track', axis=1), df_expanded], axis=1)
    df = df[['added_at', 'id', 'name', 'popularity', 'preview_url', 'album.release_date']]

    # saving the dataframe in csv format
    df.to_csv(outfile_name, index=False)
    
    return 


def create_csv_from_songs_in_playlists(sp: spotipy.Spotify, username:str, outfile_name: str, playlists_of_interest: list)-> None:
    """creates a csv file containing the playlist_id, playlist_name, track_id, track_name

    Args:
        sp (spotipy.Spotify): configured spotify object, which talks to the Spotify Web API
        username (str): username of the person, the playlists are from
        outfile_name (str): filename (with whole filepath), with which the outfile will get stored. Make sure to include also .csv at the end
        playlists_of_interest (list): list of all playlist_ids you want the csv file to contain
    """
    if os.path.exists(outfile_name):
        logger.warn('csv file already exists')
        return

    playlists = sp.user_playlists(username)

    df_all = pd.DataFrame(playlists['items'])
    df = df_all[['uri', 'name']].copy()         # just keeping the columns uri and name

    # dropping all playlists we are not interested in
    playlist_mask = [x in playlists_of_interest for x in df['uri']]
    df = df[pd.Series(playlist_mask)]
    df.reset_index(inplace=True, drop=True)
    playlist_uri_to_name_dict = df.set_index('uri').to_dict()['name']

    playlist_dict = {}
    for playlist in tqdm(df['uri'], desc='Creating csv for playlists', unit='playlists'):
        # getting all the tracks of the playlist, which could be more than 100
        playlist_dict[playlist] = dataloading.get_playlist_total_tracks(sp, username, playlist)

    dataframe_list = []     # list to hold the dataframes, which later get combined

    for i in playlist_dict:
        curr_df = pd.DataFrame(playlist_dict[i])                                    # converting the lists into a dataframe
        track_df = pd.DataFrame(curr_df['track'].to_list())                         # keeping just the track information and expanding its contents into columns
        track_df_cleaned = track_df[['id', 'name', 'popularity', 'preview_url']]    # keeping the columns we are interested in
        
        # adding a column to show the current playlist
        track_df_cleaned_added_info = track_df_cleaned.assign(playlist_id=i, 
                                                            playlist_name=playlist_uri_to_name_dict[i])
        
        dataframe_list.append(track_df_cleaned_added_info)                          # appending the created dataframe to the list

    # concatinating the dataframes into a single dataframe
    df = pd.concat(dataframe_list)
    df.rename(columns={'id': 'track_id'}, inplace=True)
    df.to_csv(outfile_name, index=False)
    
    return


def create_csv_from_songs_in_followed_artists(sp: spotipy.Spotify, outfile_name: str, artist_id_to_name: dict)-> None:
    """creates a csv file containing the artist_id, artist_name, track_id, track_name, popularity, preview_url, album.release_date for each artist in the artist_id_to_name dict

    Args:
        sp (spotipy.Spotify): spotipy object
        outfile_name (str): name you want to give the csv file (include .csv)
        artist_id_to_name (dict): dict containing the artist_id as key and the artist_name as value
    """
    if os.path.exists(outfile_name):
        logger.warn('csv file already exists')
        return
    
    # list to hold all the dataframes for each artist
    dfs = []

    # going threw all artist ids
    for curr_artist_id in tqdm(artist_id_to_name.keys(), desc='Creating followed artists csv', unit='artists'):
        curr_artist_name = artist_id_to_name[curr_artist_id]

        # getting the top tracks of the artist
        df = pd.DataFrame(sp.artist_top_tracks(artist_id=curr_artist_id)['tracks'])

        # keeping the album realase date
        df['album.release_date'] = df['album'].apply(lambda x: x['release_date'])

        # adding the artist id and name
        df['artists_id'] = curr_artist_id
        df['artist_name'] = curr_artist_name

        # renaming the id column
        df.rename(columns={'id': 'track_id'}, inplace=True)

        # appending the columns of interest to the dfs list
        dfs.append(df[['track_id', 'name', 'popularity', 'preview_url', 'album.release_date', 'artists_id', 'artist_name']])
    # saving it to a csv file
    df_final = pd.concat(dfs, axis=0).reset_index(drop=True)
    df_final.to_csv(outfile_name, index=False)

    logger.info(f'Retrieved {len(df_final)} songs for {len(artist_id_to_name)} artists.')

    return