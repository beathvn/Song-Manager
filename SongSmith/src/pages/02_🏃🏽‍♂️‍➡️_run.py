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

st.title("SongSmith - Run")

col1, col2 = st.columns(2)
with col1:
    configuration = st.file_uploader(
        "Upload your configuration file",
        type=["json"],
        label_visibility="visible",
        help="Upload the json file with your configuration.",
        accept_multiple_files=False,
    )

    if configuration is None:
        st.session_state.pop("configuration", None)

    # we just want to reload when we haven't already loaded the configuration
    # otherwise we would overwrite the changes we made in the build tab
    if configuration is not None and "configuration" not in st.session_state:
        try:
            raw = configuration.getvalue()
            text = raw.decode("utf-8")
            st.session_state.configuration = User.model_validate_json(text)
        except ValueError as e:
            st.error(f"Error loading config: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
with col2:
    tracks = st.file_uploader(
        "upload tracks table",
        type=["parquet"],
        label_visibility="visible",
        help="Upload the parquet file holding the tracks table.",
        accept_multiple_files=False,
    )
    if tracks is not None and "tracks" not in st.session_state:
        try:
            st.session_state.tracks = pd.read_parquet(tracks, engine="pyarrow")
        except ValueError as e:
            st.error(f"Error loading tracks: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

###############################################################
######################### main ################################
###############################################################

disable_create_playlist_button = configuration is None or tracks is None

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
    st.write(st.session_state.configuration)
    st.write(st.session_state.tracks)
    # TODO: implement the logic here...

col_download_config, col_download_tracks = st.columns(2)
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
with col_download_config:
    if "configuration" in st.session_state:
        st.download_button(
            label="Download configuration",
            data=st.session_state.configuration.model_dump_json(indent=2),
            file_name=f"{current_time}_config.json",
            mime="application/json",
            use_container_width=True,
        )
with col_download_tracks:
    if "tracks" in st.session_state:
        st.download_button(
            label="Download tracks table",
            data=st.session_state.tracks.to_parquet(index=False),
            file_name=f"{current_time}_tracks.parquet",
            mime="application/parquet",
            use_container_width=True,
        )
