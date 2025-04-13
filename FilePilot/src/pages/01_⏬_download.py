# 3rd party imports
import streamlit as st

# user imports
from shared.dataloading import load_yaml, write_yaml
import subprocess
import os

st.title("FilePilot - Download")

# Load configuration
config_folder = "FilePilot/config/"
config_path = os.path.join(config_folder, "download.yaml")
if "download_config" not in st.session_state:
    try:
        st.session_state.download_config = load_yaml(config_path)
    except FileNotFoundError:
        st.session_state.download_config = None


# Define callback function to update config file
def update_config():
    data_dict = st.session_state.download_config
    if data_dict is None:
        data_dict = {}
    data_dict["output_dir"] = st.session_state.output_dir
    data_dict["playlist"] = st.session_state.playlist_url
    write_yaml(config_path, data_dict)
    st.session_state.pop("download_config", None)
    st.toast("Configuration updated!", icon="✅")


with st.expander(":gear: Configuration"):
    data_dict: dict = st.session_state.download_config
    if data_dict is None:
        dir_value = ""
        playlist_value = ""
    else:
        dir_value = data_dict["output_dir"]
        playlist_value = data_dict["playlist"]

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
                    universal_newlines=True
                )
                
                # Display output in real-time
                full_output = ""
                for line in iter(process.stdout.readline, ''):
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
