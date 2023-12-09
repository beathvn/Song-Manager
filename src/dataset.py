# system imports
from argparse import ArgumentParser
import os
import math

# 3rd party imports
import pandas as pd
from tqdm import tqdm

# user imports
import helpers.dataloading as dataloading
import helpers.utils as utils


def create(config: dict):

    def create_table(table_name, columns):
        outpath = os.path.join(config['datapath'], f'{table_name}.pickle')
        if os.path.exists(outpath):
            raise ValueError(
                f'File {outpath} already exists. Delete it or run with mode "update"')
        pd.DataFrame(columns=columns).to_pickle(outpath)

    create_table('tracks', ['id', 'name', 'artists', 'preview_url'])
    create_table('tracks_fav', ['id', 'date_added', 'date_removed'])
    create_table('popularity', ['id', 'date', 'value'])
    create_table('playlists', ['id', 'track_id', 'date_added', 'date_removed'])
    create_table('playlists_names', ['id', 'name'])
    create_table('artists', ['id', 'track_id', 'date_added', 'date_removed'])
    create_table('artists_names', ['id', 'name'])


def _update_playlists_names(sp, config: dict, connection: dict):
    playlists = sp.user_playlists(connection['username'])

    df_all = pd.DataFrame(playlists['items'])
    df_playlists_names = df_all[['id', 'name']].copy(deep=True)
    del df_all

    # keeping just the playlists that we want to keep track on
    df_playlists_names = df_playlists_names[df_playlists_names.id.isin(
        list(config['playlist_to_allowed_tracks'].keys())
    )].reset_index(drop=True)
    df_playlists_names.to_pickle(os.path.join(
        config['datapath'], 'playlists_names.pickle')
    )


def _update_artists_names(sp, config):
    artists_names = {'id': [], 'name': []}

    for id in tqdm(config['artist_id_to_name'].keys(), desc='Gettings artists names'):
        artists_names['id'].append(id)
        artists_names['name'].append(sp.artist(artist_id=id)['name'])
    pd.DataFrame(artists_names).to_pickle(
        './data/spotify/artists_names.pickle')  # TODO: dont hardcode this


def _drop_trackid_duplicates(df: pd.DataFrame):
    len_before = len(df)
    df = df.drop_duplicates(subset=['track_id'], keep='first')
    if len(df) != len_before:
        df.reset_index(drop=True, inplace=True)
        print(
            f'Dropped {len_before - len(df)} duplicates from playlist {df.iloc[0]["id"]}')
    return df


def _update_popularity_and_tracks_dicts(
        df_popularity: pd.DataFrame,
        df_tracks: pd.DataFrame,
        popularity_to_add: dict,
        tracks_to_add: dict,
        current_track,
        today,
):
    track_id_curr = current_track['id']

    # update Popularity table
    if df_popularity.loc[(df_popularity.id == track_id_curr) & (df_popularity.date == today)].empty and track_id_curr not in popularity_to_add['id']:
        popularity_to_add['id'].append(track_id_curr)
        popularity_to_add['date'].append(today)
        track_popularity = current_track['popularity'] if current_track is not None else None
        popularity_to_add['value'].append(track_popularity)

    # update tracks table
    if df_tracks[df_tracks.id == track_id_curr].empty and track_id_curr not in tracks_to_add['id']:
        tracks_to_add['id'].append(track_id_curr)
        tracks_to_add['name'].append(current_track['name'])
        tracks_to_add['artists'].append(
            ', '.join([f['name'] for f in current_track['artists']]))
        tracks_to_add['preview_url'].append(current_track['preview_url'])
    return popularity_to_add, tracks_to_add


def _update_grouped_table(df_names: pd.DataFrame,
                          df_group: pd.DataFrame,
                          tracks_to_add: dict,
                          popularity_to_add: dict,
                          df_popularity: pd.DataFrame,
                          df_tracks: pd.DataFrame,
                          sp,
                          mode: str,
                          connection: dict
):
    """A groud can be playlists or artists
    """
    today = pd.Timestamp.today().date()
    lst_group_new = []

    # NOTE: maybe use parallel processing here
    for _, row in tqdm(df_names.iterrows(), total=len(df_names), desc='Going through groups'):
        #################### going through the current group ####################
        # one group at a time
        df_current_group = df_group[df_group.id == row.id]
        df_current_group = _drop_trackid_duplicates(df_current_group)
        group_to_add = {'id': [], 'track_id': [],
                        'date_added': [], 'date_removed': []}

        if mode == 'playlists':
            group_tracks = dataloading.get_playlist_total_tracks(
                sp=sp,
                username=connection['username'],
                playlist_id=row.id,
            )
            track_ids_present = [f['track']['id']
                                 for f in group_tracks if f['track'] is not None]
        elif mode == 'artists':
            group_tracks = sp.artist_top_tracks(artist_id=row.id)['tracks']
            track_ids_present = [f['id']
                                 for f in group_tracks if f['id'] is not None]
        else:
            raise ValueError('Mode must be either "playlists" or "artists"')

        # add date_removed information
        df_current_group.loc[~df_current_group.track_id.isin(
            track_ids_present), 'date_removed'] = today

        #################### going through the songs in the current group group ####################
        for index, current_track in tqdm(enumerate(group_tracks), total=len(group_tracks), desc='Going through current group songs'):
            # going through the tracks in the current playlist

            track_id_curr = track_ids_present[index]
            df_ = df_current_group.loc[(df_current_group.track_id == track_id_curr) & (
                df_current_group.date_removed.isnull())]
            if not df_.empty:
                assert len(df_) == 1, 'There should be only one row'
            else:
                if mode == 'playlists':
                    current_track = current_track['track']
                assert current_track['id'] == track_id_curr, 'The track_ids must match'

                # we cannot use the date_added in playlist, since there are playlists, where that info is not trustable
                group_to_add['date_added'].append(today)

                group_to_add['id'].append(row.id)
                group_to_add['track_id'].append(track_id_curr)
                group_to_add['date_removed'].append(None)

                popularity_to_add, tracks_to_add = _update_popularity_and_tracks_dicts(
                    df_popularity, df_tracks, popularity_to_add, tracks_to_add, current_track, today)

        lst_group_new.append(
            pd.concat([df_current_group, pd.DataFrame(group_to_add)], ignore_index=True))

    df_group = pd.concat(lst_group_new, ignore_index=True)
    df_group.date_added = pd.to_datetime(df_group.date_added).dt.date
    df_group.date_removed = pd.to_datetime(df_group.date_removed).dt.date
    return df_group, tracks_to_add, popularity_to_add


def _update_tracks_fav(
        sp,
        df_tracks_fav: pd.DataFrame,
        tracks_to_add: dict,
        popularity_to_add: dict,
        df_popularity: pd.DataFrame,
        df_tracks: pd.DataFrame,
):
    results = []

    # Loop through the results until we have retrieved all tracks
    total_tracks = sp.current_user_saved_tracks(limit=1, offset=0)['total']
    # 50 is the max amount you can fetch in a single request
    iterations = math.ceil(total_tracks / 50)

    for curr_iteration in tqdm(range(iterations), desc='Updating favourite tracks table', unit='packs of 50 songs'):
        track_results = sp.current_user_saved_tracks(
            limit=50, offset=curr_iteration * 50)

        # Add the retrieved tracks to our results list
        results += track_results['items']

    print(f"Retrieved {len(results)} saved tracks.")

    track_ids_present = [f['track']['id']
                         for f in results if f['track']['id'] is not None]

    track_fav_to_add = {'id': [], 'date_added': [], 'date_removed': []}
    today = pd.Timestamp.today().date()
    df_tracks_fav.loc[~df_tracks_fav.id.isin(
        track_ids_present), 'date_removed'] = today

    for current_track in tqdm(results, total=len(results), desc='Going through the favourite songs'):
        # going through the tracks

        track_id_curr = current_track['track']['id']
        df_ = df_tracks_fav.loc[(df_tracks_fav.id == track_id_curr) & (
            df_tracks_fav.date_removed.isnull())]
        if not df_.empty:
            assert len(df_) == 1, 'There should be only one row'
        else:
            track_fav_to_add['date_added'].append(current_track['added_at'])
            current_track = current_track['track']
            assert current_track['id'] == track_id_curr, 'The track_ids must match'

            track_fav_to_add['id'].append(track_id_curr)
            track_fav_to_add['date_removed'].append(None)

            popularity_to_add, tracks_to_add = _update_popularity_and_tracks_dicts(
                df_popularity, df_tracks, popularity_to_add, tracks_to_add, current_track, today)

    df_tracks_fav = pd.concat(
        [df_tracks_fav, pd.DataFrame(track_fav_to_add)], ignore_index=True)
    df_tracks_fav.date_added = pd.to_datetime(df_tracks_fav.date_added).dt.date
    df_tracks_fav.date_removed = pd.to_datetime(
        df_tracks_fav.date_removed).dt.date
    return df_tracks_fav, tracks_to_add, popularity_to_add


def update(config: dict, connection: dict):
    sp = utils.get_auth_spotipy_obj(connection, scope='user-library-read')

    ############ tracks and popularity tables ############
    _update_playlists_names(sp, config, connection)
    _update_artists_names(sp, config)

    df_tracks = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks.pickle'))
    tracks_to_add = {'id': [], 'name': [], 'artists': [], 'preview_url': []}

    df_popularity = pd.read_pickle(os.path.join(
        config['datapath'], 'popularity.pickle'))
    popularity_to_add = {'id': [], 'date': [], 'value': []}

    ############ playlists and artists table ############

    df_playlists = pd.read_pickle(os.path.join(
        config['datapath'], 'playlists.pickle'))
    df_playlists_names = pd.read_pickle(os.path.join(
        config['datapath'], 'playlists_names.pickle'))

    df_playlists, tracks_to_add, popularity_to_add = _update_grouped_table(
        df_names=df_playlists_names,
        df_group=df_playlists,
        tracks_to_add=tracks_to_add,
        popularity_to_add=popularity_to_add,
        df_popularity=df_popularity,
        df_tracks=df_tracks,
        sp=sp,
        mode='playlists',
        connection=connection,
    )
    df_playlists.to_pickle(os.path.join(
        config['datapath'], 'playlists.pickle'))

    df_artists = pd.read_pickle(os.path.join(
        config['datapath'], 'artists.pickle'))
    df_artists_names = pd.read_pickle(os.path.join(
        config['datapath'], 'artists_names.pickle'))

    df_artists, tracks_to_add, popularity_to_add = _update_grouped_table(
        df_names=df_artists_names,
        df_group=df_artists,
        tracks_to_add=tracks_to_add,
        popularity_to_add=popularity_to_add,
        df_popularity=df_popularity,
        df_tracks=df_tracks,
        sp=sp,
        mode='artists',
        connection=connection,
    )
    df_artists.to_pickle(os.path.join(config['datapath'], 'artists.pickle'))

    ############ tracks_fav table ############
    df_tracks_fav = pd.read_pickle(os.path.join(
        config['datapath'], 'tracks_fav.pickle'))

    df_tracks_fav, tracks_to_add, popularity_to_add = _update_tracks_fav(
        df_tracks_fav=df_tracks_fav,
        tracks_to_add=tracks_to_add,
        popularity_to_add=popularity_to_add,
        df_popularity=df_popularity,
        df_tracks=df_tracks,
        sp=sp,
    )
    df_tracks_fav.to_pickle(os.path.join(
        config['datapath'], 'tracks_fav.pickle'))

    ############ writing tracks and popularity table ############
    pd.concat([
        df_popularity,
        pd.DataFrame(popularity_to_add)],
        ignore_index=True).to_pickle(os.path.join(config['datapath'], 'popularity.pickle'))

    pd.concat([
        df_tracks,
        pd.DataFrame(tracks_to_add)],
        ignore_index=True).to_pickle(os.path.join(config['datapath'], 'tracks.pickle'))


if __name__ == "__main__":
    print('Start of program: dataset.py...')
    parser = ArgumentParser()
    parser.add_argument('-m', '--mode', required=True)
    parser.add_argument(
        '-c', '--config', default='./config/spotiplaylist.yaml')
    parser.add_argument(
        '-n', '--connection', default='./config/connection.yaml')
    args = parser.parse_args()

    config = dataloading.load_yaml(args.config)
    connection = dataloading.load_yaml(args.connection)

    if args.mode == 'create':
        print('Creating dataset from scratch...')
        create(config)
        update(config, connection)
    elif args.mode == 'update':
        print('Updating dataset...')
        update(config, connection)
    else:
        raise ValueError('Mode must be either "create" or "update"')

    print('End of program: dataset.py')
