# system imports
import os
from datetime import date

# 3rd party imports
import streamlit as st
import pandas as pd
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# user imports
from entities import *

def _get_spotify_obj(user: User, scop: str) -> spotipy.Spotify:
    """Get the Spotify object with the given scope"""
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scop,
            **user.auth.model_dump(),
        ),
    )


st.title("SongSmith - Run")

col1, col2 = st.columns(2)
with col1:
    user = st.file_uploader(
        "Upload your configuration file",
        type=["json"],
        label_visibility="visible",
        help="Upload the json file with your configuration.",
        accept_multiple_files=False,
    )
        
    # we just want to reload when we haven't already loaded the user
    # otherwise we would overwrite the changes we made in the build tab
    if user is not None:
        try:
            raw = user.getvalue()
            text = raw.decode("utf-8")
            st.session_state.user = User.model_validate_json(text)
        except ValueError as e:
            st.error(f"Error loading config: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    else:
        st.session_state.pop("user", None)
with col2:
    tracks = st.file_uploader(
        "upload tracks table",
        type=["parquet"],
        label_visibility="visible",
        help="Upload the parquet file holding the tracks table.",
        accept_multiple_files=False,
    )
    if tracks is not None:
        try:
            st.session_state.tracks = pd.read_parquet(tracks, engine="pyarrow")
        except ValueError as e:
            st.error(f"Error loading tracks: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    else:
        st.session_state.pop("tracks", None)

###############################################################
######################### main ################################
###############################################################

disable_create_playlist_button = user is None or tracks is None

if disable_create_playlist_button:
    st.warning(
        ":warning: Please upload the configuration file and the tracks table to proceed."
    )
if st.button(
    "Create new songs playlists",
    disabled=disable_create_playlist_button,
    use_container_width=True,
    type="primary",
):
    df_tracks: pd.DataFrame = st.session_state.tracks
    user: User = st.session_state.user

    sp = _get_spotify_obj(user, "user-library-read")

    ###############################################################
    ################ update fav tracks ############################
    ###############################################################
    results = []

    iteration = 0
    continue_to_go_back = True
    while True:
        track_results = sp.current_user_saved_tracks(
            limit=50, offset=iteration * 50)
        results += track_results['items']
        ids = [track["track"]["id"] for track in results]

        # we don't look just in the favorites - as soon we find a track that is already in the database, we stop
        if df_tracks[df_tracks["id"].isin(ids)].shape[0] > 0:
            break
        iteration += 1


    possible_new_tracks = tracks_list = [Track(
        id=track["track"]["id"],
        name=track["track"]["name"],
        artist_ids=[artist["id"] for artist in track["track"]["artists"]],
        artist_names=[artist["name"] for artist in track["track"]["artists"]],
        date_added=datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ").date(),
        added_from="favorites"
    ) for track in results]

    # concatenate the new tracks, where the id is not in the database
    new_tracks = [track for track in possible_new_tracks if track.id not in df_tracks["id"].values]
    if len(new_tracks) > 0:
        st.toast(f"Found {len(new_tracks)} new tracks", icon="✅")
        df_new_tracks = pd.DataFrame([vars(track) for track in new_tracks])
        df_tracks = pd.concat([df_new_tracks, df_tracks])
        df_tracks.reset_index(drop=True, inplace=True)
    else:
        st.toast("No new tracks found", icon="⚠️")
    
    ###############################################################
    ####### add the latest tracks from playlists / artists ########
    ###############################################################

    # this will hold the dataframes of the tracks to add
    tracks_to_add = []
    today_str = date.today().strftime("%Y-%m-%d")

    for playlist in user.playlists:
        tracks_in_playlist = []
        tot_tracks = sp.playlist(playlist.id, fields="tracks.total")["tracks"]["total"]
        batch_size = 100

        for offset in range(0, tot_tracks, batch_size):
            tracks = sp.playlist_items(
                playlist.id,
                limit=batch_size,
                offset=offset,
                fields="items(track(id, popularity)",
            )["items"]
            tracks_in_playlist.extend([t["track"] for t in tracks])
        
        df_tracks_playlist = pd.DataFrame(tracks_in_playlist)
        df_tracks_playlist = df_tracks_playlist[~df_tracks_playlist["id"].isin(df_tracks["id"])]
        df_tracks_playlist.sort_values(by="popularity", ascending=False, inplace=True)
        df_tracks_playlist.drop(columns=["popularity"], inplace=True)
        df_tracks_playlist["added_from"] = playlist.id
        df_tracks_playlist["date_added"] = today_str
        tracks_to_add.append(df_tracks_playlist.iloc[:playlist.allowed_tracks])
    
    all_track_dfs = [df_tracks] + tracks_to_add
    df_tracks_new = pd.concat(all_track_dfs, ignore_index=True, sort=False)
    def populate_null(row):
        if row.isnull().any():
            # TODO: continue here: populate the null values
            pass
        else:
            return row
    df_filled = df_tracks_new.apply(populate_null, axis=1)


# TODO: this should download the df_filled... not the df_tracks
if "tracks" in st.session_state:
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    st.download_button(
        label="Download tracks table",
        data=st.session_state.tracks.to_parquet(index=False),
        file_name=f"{current_time}_tracks.parquet",
        mime="application/parquet",
        use_container_width=True,
    )
