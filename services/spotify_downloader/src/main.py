# export the found on the road playlist to .csv file

# system imports
import argparse
import logging
import os

# 3rd party imports
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# local imports
from song_common.logging_config import setup_logging
from spotify_client.entities import User


def main(playlist_url: str, output_folder: str, config_path: str) -> None:
    logger = logging.getLogger("spotify_downloader")
    logger.setLevel(logging.INFO)

    logger.info(f"Saving playlist: {playlist_url}")

    with open(config_path, "r") as f:
        user = User.model_validate_json(f.read())

    os.environ["SPOTIPY_CLIENT_ID"] = user.auth.client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = user.auth.client_secret
    os.environ["SPOTIPY_REDIRECT_URI"] = user.auth.redirect_uri

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
    setup_logging()

    ################## step 0 ##################

    parser = argparse.ArgumentParser(
        description="Export Spotify playlist tracks to CSV"
    )
    parser.add_argument("--playlist-url", help="Spotify playlist URL")
    parser.add_argument(
        "--output-folder",
        help="Output folder for CSV file",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration JSON file",
    )

    args = parser.parse_args()

    main(args.playlist_url, args.output_folder, args.config)
