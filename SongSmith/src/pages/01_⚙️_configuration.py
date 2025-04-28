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

###############################################################
################# general functions ###########################
###############################################################


def _get_spotify_obj(user: User, scop: str) -> spotipy.Spotify:
    """Get the Spotify object with the given scope"""
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scop,
            **user.auth.model_dump(),
        ),
    )


def get_playlist_id_name(user: User, playlist_url: str) -> tuple[str, str]:
    """Get the playlist ID and name from the URL
    Return None when error happens
    """
    try:
        sp = _get_spotify_obj(user, "user-library-read")
        playlist = sp.playlist(playlist_url)
        return playlist["id"], playlist["name"]
    except Exception as e:
        st.error(f"Error fetching playlist: {e}")
        return None, None


def get_artist_id_name(user: User, artist_url: str) -> tuple[str, str]:
    """Get the artist ID and name from the URL
    Return None when error happens
    """
    try:
        sp = _get_spotify_obj(user, "user-library-read")
        artist = sp.artist(artist_url)
        return artist["id"], artist["name"]
    except Exception as e:
        st.error(f"Error fetching artist: {e}")
        return None, None


st.title("SongSmith - Configuration")


###############################################################
################# init session state ##########################
###############################################################

if "playlist_editor_key" not in st.session_state:
    st.session_state.playlist_editor_key = 0

if "artist_editor_key" not in st.session_state:
    st.session_state.artist_editor_key = -1

if "playlists_autopopulated" not in st.session_state:
    st.session_state.playlists_autopopulated = None

if "artists_autopopulated" not in st.session_state:
    st.session_state.artists_autopopulated = None

###############################################################
################# main functionality ##########################
###############################################################"

build_config = st.file_uploader(
    "Upload your configuration file",
    type=["json"],
    label_visibility="visible",
    help="Upload the json file with you want to change",
    accept_multiple_files=False,
)

if build_config is not None:
    try:
        raw = build_config.getvalue()
        text = raw.decode("utf-8")
        st.session_state.build_config = User.model_validate_json(text)
    except ValueError as e:
        st.error(f"Error loading config: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
if build_config is None:
    st.session_state.build_config = User(
        id="",
        auth=Authentication(
            client_id="",
            client_secret="",
            redirect_uri="",
        ),
        spotify_user_name="",
        playlists=[],
        artists=[],
    )
    st.session_state.playlists_autopopulated = None

st.divider()

user: User = st.session_state.build_config

with st.expander("🔑 Spotify API Authentication", expanded=False):
    st.markdown(
        "you can find this information in the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications)"
    )
    client_id = st.text_input(
        "Spotify Client ID",
        value=user.auth.client_id,
    )
    if client_id != user.auth.client_id:
        user.auth.client_id = client_id

    client_secret = st.text_input(
        "Spotify Client Secret",
        type="password",
        value=user.auth.client_secret,
    )
    if client_secret != user.auth.client_secret:
        user.auth.client_secret = client_secret
    redirect_uri = st.text_input(
        "Spotify Redirect URI",
        placeholder="http://localhost:8080",
        value=user.auth.redirect_uri,
    )
    if redirect_uri != user.auth.redirect_uri:
        user.auth.redirect_uri = redirect_uri

spotify_user_name = st.text_input(
    "Spotify User Name",
    value=user.spotify_user_name,
    help="This is the username you use to log in to Spotify",
)
if spotify_user_name != user.spotify_user_name:
    user.spotify_user_name = spotify_user_name

st.divider()
st.markdown("## Playlists")
if st.session_state.playlists_autopopulated is not None:
    if not st.session_state.playlists_autopopulated.isnull().values.any():
        user.playlists = [
            CatalogItem.model_validate(record)
            for record in st.session_state.playlists_autopopulated.to_dict(
                orient="records"
            )
        ]
    else:
        st.toast("there was probably an error in the autopopulate process", icon="❌")
        st.session_state.playlists_autopopulated = None

df_playlists_edited: pd.DataFrame = st.data_editor(
    user.playlists_df,
    key=st.session_state.playlist_editor_key,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
)

if not df_playlists_edited.isnull().values.any():
    user.playlists = [
        CatalogItem.model_validate(record)
        for record in df_playlists_edited.to_dict(orient="records")
    ]

if st.button(
    "autopopulate playlists",
    use_container_width=True,
    help="This will autopopulate the **name** and **id** columns - enabled when there are null values",
    disabled=not df_playlists_edited.isnull().values.any(),
):
    if df_playlists_edited.isnull().values.any():
        null_in_allowed_tracks = df_playlists_edited["allowed_tracks"].isnull().any()
        null_in_url = df_playlists_edited["url"].isnull().any()
        if null_in_allowed_tracks or null_in_url:
            st.toast("can just autopopulate **name** and **id**", icon="⚠️")
        else:
            with st.spinner("Fetching playlist information..."):
                progress_bar = st.progress(0)
                total_rows = len(
                    df_playlists_edited[
                        df_playlists_edited["id"].isnull()
                        | df_playlists_edited["name"].isnull()
                    ]
                )
                processed = 0

                for i, row in df_playlists_edited.iterrows():
                    if pd.isna(row["id"]) or pd.isna(row["name"]):
                        playlist_id, playlist_name = get_playlist_id_name(
                            user, row["url"]
                        )
                        df_playlists_edited.at[i, "id"] = playlist_id
                        df_playlists_edited.at[i, "name"] = playlist_name

                        processed += 1
                        progress_bar.progress(processed / total_rows)

                progress_bar.empty()

            st.session_state.playlist_editor_key += 1
            st.session_state.playlists_autopopulated = df_playlists_edited
            st.rerun()
    else:
        st.toast("No null values in the playlist table.", icon="⚠️")

###############################################################
#################### artists ##################################
###############################################################

st.markdown("## Artists")
if st.session_state.artists_autopopulated is not None:
    if not st.session_state.artists_autopopulated.isnull().values.any():
        user.artists = [
            CatalogItem.model_validate(record)
            for record in st.session_state.artists_autopopulated.to_dict(
                orient="records"
            )
        ]
    else:
        st.toast("there was probably an error in the autopopulate process", icon="❌")
        st.session_state.artists_autopopulated = None

df_artists_edited: pd.DataFrame = st.data_editor(
    user.artists_df,
    key=st.session_state.artist_editor_key,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
)

if not df_artists_edited.isnull().values.any():
    user.artists = [
        CatalogItem.model_validate(record)
        for record in df_artists_edited.to_dict(orient="records")
    ]

if st.button(
    "autopopulate artists",
    help="This will autopopulate the **name** and **id** columns - enabled when there are null values",
    disabled=not df_artists_edited.isnull().values.any(),
    use_container_width=True,
):
    if df_artists_edited.isnull().values.any():
        null_in_allowed_tracks = df_artists_edited["allowed_tracks"].isnull().any()
        null_in_url = df_artists_edited["url"].isnull().any()
        if null_in_allowed_tracks or null_in_url:
            st.toast("can just autopopulate **name** and **id**", icon="⚠️")
        else:
            with st.spinner("Fetching playlist information..."):
                progress_bar = st.progress(0)
                total_rows = len(
                    df_artists_edited[
                        df_artists_edited["id"].isnull()
                        | df_artists_edited["name"].isnull()
                    ]
                )
                processed = 0

                for i, row in df_artists_edited.iterrows():
                    if pd.isna(row["id"]) or pd.isna(row["name"]):
                        artist_id, artist_name = get_artist_id_name(user, row["url"])
                        df_artists_edited.at[i, "id"] = artist_id
                        df_artists_edited.at[i, "name"] = artist_name

                        processed += 1
                        progress_bar.progress(processed / total_rows)

                progress_bar.empty()

            st.session_state.artist_editor_key -= 1
            st.session_state.artists_autopopulated = df_artists_edited
            st.rerun()
    else:
        st.toast("No null values in the artist table.", icon="⚠️")

st.download_button(
    "⬇️ Download updated configuration",
    user.model_dump_json(indent=2),
    file_name=f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_config.json",
    mime="application/json",
    help="This will download the current configuration as a json file. (will be disabled if there are null values in the table)",
    use_container_width=True,
    type="primary",
    # disabled=disable_download_button,
)

st.divider()

###############################################################
#################### artists ##################################
###############################################################

disable_init_tracks = client_id == "" or client_secret == "" or redirect_uri == "" or spotify_user_name == ""

if st.button(
    "Init tracks table",
    use_container_width=True,
    help="This will create a new tracks table based on your favorites - disabled on missing infos",
    disabled=disable_init_tracks,
):
    # TODO: when i don't have the parquet file, i can't start working...
    pass