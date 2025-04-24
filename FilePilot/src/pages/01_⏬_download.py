# system imports
import os

# 3rd party imports
import streamlit as st

# user imports
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess

# local imports
from shared.dataloading import load_yaml, write_yaml


st.title("FilePilot - Download")

# Load configuration
config_folder = "FilePilot/config/"
config_path = os.path.join(config_folder, "download.yaml")
if "download_config" not in st.session_state:
    try:
        st.session_state.download_config = load_yaml(config_path)
    except FileNotFoundError:
        st.session_state.download_config = None


def get_playlist_name(playlist_url: str) -> str:
    if playlist_url == "":
        return "UNDEFINED"

    load_dotenv(f"FilePilot/.env", override=True)
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI")
    if client_id is None or client_secret is None or redirect_uri is None:
        st.error("Please set up your Spotify API credentials in the .env file.")
        return "MISSING"
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    return sp.playlist(playlist_url)["name"]


# Define callback function to update config file
def update_config():
    data_dict = st.session_state.download_config
    if data_dict is None:
        data_dict = {}
    data_dict["output_dir"] = st.session_state.output_dir
    data_dict["playlist"] = st.session_state.playlist_url
    data_dict["playlist_name"] = get_playlist_name(st.session_state.playlist_url)

    write_yaml(config_path, data_dict)
    st.session_state.pop("download_config", None)
    st.toast("Configuration updated!", icon="✅")


with st.expander(":gear: Configuration"):
    data_dict: dict = st.session_state.download_config
    if data_dict is None:
        dir_value = ""
        playlist_value = ""
        playlist_name = "UNDEFINED"
    else:
        dir_value = data_dict["output_dir"]
        playlist_value = data_dict["playlist"]
        playlist_name = data_dict["playlist_name"]

    st.text_input(
        "output directory:",
        value=dir_value,
        key="output_dir",
        on_change=update_config,
    )

    st.text_input(
        "playlist URL:",
        value=playlist_value,
        key="playlist_url",
        on_change=update_config,
    )

    st.markdown(f"-> Playlist name: **{playlist_name}**")

if st.button("⏬ Download Songs"):
    output_dir = st.session_state.output_dir
    playlist_url = st.session_state.playlist_url
    if output_dir == "" or output_dir == "":
        st.error("First, make sure the configuration is set up correctly.")
    else:
        # Format the command
        cmd = ["spotdl", playlist_url, "--output", output_dir, "--bitrate", "128k"]

        # Create a placeholder for live output
        output_placeholder = st.empty()

        # Show in progress message
        with st.spinner("Downloading songs from Spotify..."):
            try:
                # Execute the spotdl command with real-time output
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                )

                # Display output in real-time
                full_output = ""
                for line in iter(process.stdout.readline, ""):
                    full_output += line
                    output_placeholder.code(full_output)

                process.stdout.close()
                return_code = process.wait()

                if return_code == 0:
                    st.success("Download completed successfully!")
                else:
                    st.error("Download failed")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
