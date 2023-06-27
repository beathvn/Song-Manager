# This scripts holds different functions to help processing different data


# 3rd party imports
import pandas as pd

# user imports
from logger import logger


def adding_pre_and_post_str(pre: str, post: str, my_list: list)-> list:
    """adds the pre and post string to each entry of the given list.
    A blank space is added in the form: pre + ' ' + TEXT + ' ' + post

    Args:
        pre (str): string to add in front
        post (str): string to add at the end
        my_list (list): list holding entries you want to extend by pre and post

    Returns:
        list: new list holding the changed values
    """
    return [pre + ' ' + i +
            ' ' + post for i in my_list]


def remove_illegal_characters(item: any)-> any:
    """removes the characters ['(', ')', '\'', '&'] from item.
    item can be string or list. 
    If type is list, every element will have the illegal characters removed.

    Args:
        item (any): item you want the illegal characters to be removed

    Raises:
        NotImplementedError: when item is something else than list or string

    Returns:
        any: same datatype as input
    """
    if len(item) == 0:
        return item
    
    # removing the characters ytmdl cannot handle
    illegal_characters = ['(', ')', '\'', '&']

    if isinstance(item, list):
        for illegal_character in illegal_characters:
            item = [i.replace(illegal_character, '') for i in item]
    elif isinstance(item, str):
        for illegal_character in illegal_characters:
            item = item.replace(illegal_character, '')
    else:
        raise NotImplementedError('cannot handle other datatype than string or list')

    return item


def filter_df_new_arrivals(df_old: pd.DataFrame, df_new: pd.DataFrame)-> pd.DataFrame:
    """Creates a new DataFrame containing just the new songs present in df_new, but not in df_old.

    Args:
        df_old (pd.DataFrame): holding the old playlist songs
        df_new (pd.DataFrame): holding the new playlist songs

    Returns:
        pd.DataFrame: containing just the newly added songs
    """
    # make sure that if we have a new song, which gets added to multiple playlists, we dont drop it afterwards
    df_new.drop_duplicates(subset='track_id', keep='first', inplace=True)

    df_new_arrivals = pd.concat([df_old, df_new]).reset_index(drop=True)
    df_new_arrivals.drop_duplicates(subset=['track_id'], keep=False, inplace=True)

    # fixing the index
    df_new_arrivals.reset_index(inplace=True, drop=True)

    return df_new_arrivals


def remove_saved_tracks_from_df(df: pd.DataFrame, saved_track_ids: set)-> pd.DataFrame:
    """Drops the already saved tracks from df

    Args:
        df (pd.DataFrame): the DataFrame you want to remove the tracks
        saved_track_ids (set): the track_ids you want to remove

    Returns:
        pd.DataFrame: a new dataframe with the given track_ids removed
    """

    df_filtered = df[~df['track_id'].isin(saved_track_ids)]
    
    old_len = len(df)
    new_len = len(df_filtered)
    
    if old_len != new_len:
        logger.info(f'Dropped {old_len - new_len} tracks, which are already saved')
    else:
        logger.info('No tracks which were already saved, dropped.')
    
    return df_filtered


def limit_df_count(df:pd.DataFrame, dict_playlist_limits: dict, dict_uri_to_name: dict)-> pd.DataFrame:
    """Limits the amount of df by taking into consideration the popularity of songs and the given max. number in dict_playlist_limits

    Args:
        df (pd.DataFrame): DataFrame you want to reduce the size of
        dict_playlist_limits (dict): keys are the playlist ids and value is the allowed tracks to be added
        dict_uri_to_name (dict): keys are the playlist uris and value is the actual name of the playlist

    Returns:
        pd.DataFrame: limited dataframe
    """
    # list to hold the dataframe for each playlist, which in the end get combined
    sub_dfs = []

    for curr_playlist in dict_playlist_limits:
        curr_df = df[df['playlist_id'] == curr_playlist].copy()

        # sorting the values on popularity
        curr_df.sort_values('popularity', ascending=False, inplace=True)

        len_full = len(curr_df)
        len_allowed = dict_playlist_limits[curr_playlist]

        # limiting the amount
        if len_full > len_allowed:
            sub_dfs.append(curr_df[:len_allowed])
            logger.warn(f'{len_full} new songs found in \t{dict_uri_to_name[curr_playlist]},\tbut added just {len_allowed} due to limitation.')
        else:
            logger.info(f'{len_full} new songs found in \t{dict_uri_to_name[curr_playlist]},\tadded ALL')
            sub_dfs.append(curr_df)

    df_thin = pd.concat(sub_dfs)
    df_thin.reset_index(inplace=True, drop=True)

    return df_thin