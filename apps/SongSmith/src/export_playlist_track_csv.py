# system imports
import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path - make sure we can import shared modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 3rd party imports
from dotenv import load_dotenv
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# local imports
from shared.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Export Spotify playlist tracks to CSV"
    )
    parser.add_argument("--env-file", help="Path to .env file")
    parser.add_argument("--playlist_url", help="Spotify playlist URL")
    parser.add_argument(
        "--output-folder",
        help="Output folder for CSV file",
    )
    # add the env file path
    args = parser.parse_args()

    playlist_url = args.playlist_url
    output_folder = args.output_folder
    env_file = args.env_file

    logger.info(f"Processing playlist: {playlist_url}")

    # getting the environmental variables

    try:
        load_dotenv(env_file, override=True)
        _ = os.environ["SPOTIPY_CLIENT_ID"]
        _ = os.environ["SPOTIPY_CLIENT_SECRET"]
        _ = os.environ["SPOTIPY_REDIRECT_URI"]
    except KeyError as e:
        logger.error(f"Environment variable {e} not found.")
        return

    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    playlist = sp.playlist(playlist_url)
    logger.info(
        "Found playlist:"
        + playlist["name"]
        + " with "
        + str(playlist["tracks"]["total"])
        + " tracks."
    )

    data_out = {"name": [], "artists": [], "uri": []}
    for item in playlist["tracks"]["items"]:
        track = item["track"]
        data_out["name"].append(track["name"])
        data_out["artists"].append(
            ";".join([artist["name"] for artist in track["artists"]])
        )
        data_out["uri"].append(track["uri"])

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    output_path = os.path.join(output_folder, f"{today}.csv")
    pd.DataFrame(data_out).to_csv(output_path, index=False)
    logger.info(f"CSV file saved to {output_path}")


if __name__ == "__main__":
    main()
