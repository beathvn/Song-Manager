# system imports
import os
import argparse
from datetime import date, datetime
import logging

# 3rd party imports
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

# private library imports
from spotify_client.entities import User, Track
from song_common.logging_config import setup_logging


def main(config_path: str, database_folder: str) -> None:
    logger = logging.getLogger("spotify_discovery")
    logger.setLevel(logging.INFO)
    with open(config_path, "r") as f:
        user = User.model_validate_json(f.read())

    ################## step 1 ##################
    # read tracks table
    df_tracks = pd.read_parquet(os.path.join(database_folder, "latest_tracks.parquet"))

    ################## step 2 ##################
    os.environ["SPOTIPY_CLIENT_ID"] = user.auth.client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = user.auth.client_secret
    os.environ["SPOTIPY_REDIRECT_URI"] = user.auth.redirect_uri

    # find the most recently added favorite track
    idx = df_tracks.loc[df_tracks["added_from"] == "favorites", "date_added"].idxmax()
    latest_fav_id = df_tracks.loc[idx, "id"]
    logger.info(f"latest favorite track id: {latest_fav_id}")

    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # empirically we see, that the results are ordered by most recently added first
    results = []
    offset = 0

    while True:
        page = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = page["items"]
        if not items:
            logger.debug("no more items for favorites")
            break

        for item in items:
            tid = item["track"]["id"]
            if tid == latest_fav_id:
                break  # reached the point
            results.append(item)

        else:
            # runs only if the inner loop did NOT break
            offset += 50
            if offset >= 150:  # safety break
                raise RuntimeError(
                    "Latest favorite not found within 150 tracks. "
                    "State is inconsistent (track likely removed)."
                )

            continue

        break  # found latest_fav_id inside the page

    existing_ids = set(df_tracks["id"])

    new_fav_tracks = [
        Track(
            id=track["track"]["id"],
            name=track["track"]["name"],
            artist_ids=[artist["id"] for artist in track["track"]["artists"]],
            artist_names=[artist["name"] for artist in track["track"]["artists"]],
            date_added=datetime.strptime(
                track["added_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).date(),
            added_from="favorites",
        )
        for track in results
        if track["track"]["id"] not in existing_ids
    ]

    # preparing for concatenation
    new_fav_tracks = pd.DataFrame([f.model_dump() for f in new_fav_tracks])

    ################## step 3 ##################
    today = date.today()
    new_pla_tracks = []

    for playlist in tqdm(user.playlists, desc="Playlists"):
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
        df_tracks_playlist = df_tracks_playlist[
            ~df_tracks_playlist["id"].isin(df_tracks["id"])
        ]
        df_tracks_playlist.sort_values(by="popularity", ascending=False, inplace=True)
        df_tracks_playlist.drop(columns=["popularity"], inplace=True)
        df_tracks_playlist["added_from"] = f"pla:{playlist.id}"
        df_tracks_playlist["date_added"] = today
        if df_tracks_playlist.empty:
            logger.debug(f"playlist done (no new tracks): {playlist.name}")
            continue

        new_pla_tracks.append(df_tracks_playlist.iloc[: playlist.allowed_tracks])
        logger.debug(f"playlist done: {playlist.name}")
    new_art_tracks = []
    for artist in tqdm(user.artists, desc="Artists"):
        # just keep the relevant fields
        tracks_in_artist = [
            {
                "id": track["id"],
                "name": track["name"],
                "popularity": track["popularity"],
                "artist_ids": [artist["id"] for artist in track["artists"]],
                "artist_names": [artist["name"] for artist in track["artists"]],
            }
            for track in sp.artist_top_tracks(artist.id)["tracks"]
        ]

        df_tracks_artist = pd.DataFrame(tracks_in_artist)
        df_tracks_artist = df_tracks_artist[~df_tracks_artist["id"].isin(existing_ids)]
        df_tracks_artist.sort_values(by="popularity", ascending=False, inplace=True)
        df_tracks_artist.drop(columns=["popularity"], inplace=True)
        df_tracks_artist["added_from"] = f"art:{artist.id}"
        df_tracks_artist["date_added"] = today
        if df_tracks_artist.empty:
            logger.debug(f"artist done (no new tracks): {artist.name}")
            continue

        new_art_tracks.append(df_tracks_artist.iloc[: artist.allowed_tracks])

        logger.debug(f"artist done: {artist.name}")

    ################## step 4 ##################
    df_tracks_updated: pd.DataFrame = pd.concat(
        [df_tracks] + [new_fav_tracks] + new_pla_tracks + new_art_tracks,
        ignore_index=True,
    )

    # drop potential duplicates (in case that artist and playlist added the same track)
    len_before = len(df_tracks_updated)
    df_tracks_updated.drop_duplicates(subset=["id"], inplace=True)
    len_after = len(df_tracks_updated)
    if len_before != len_after:
        logger.info(
            f"Dropped {len_before - len_after} duplicate tracks when merging new tracks."
        )

    ################## step 5 ##################
    def populate_null(row):
        if row.isnull().any():
            curr_track = sp.track(row["id"])
            row["name"] = curr_track["name"]
            row["artist_ids"] = [artist["id"] for artist in curr_track["artists"]]
            row["artist_names"] = [artist["name"] for artist in curr_track["artists"]]
            return row
        else:
            return row

    # NOTE: apply with axis=1 can be slow for large dataframes - but here it's acceptable
    df_tracks_updated: pd.DataFrame = df_tracks_updated.apply(populate_null, axis=1)

    ################## step 6 ##################
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    df_tracks_updated.to_parquet(
        os.path.join(database_folder, f"{current_time}_tracks.parquet"), index=False
    )
    df_tracks_updated.to_parquet(
        os.path.join(database_folder, "latest_tracks.parquet"), index=False
    )

    ################ step 7 ##################
    df_for_playlist = df_tracks_updated[df_tracks_updated["date_added"] == today]
    df_for_playlist = df_for_playlist[df_for_playlist["added_from"] != "favorites"]

    cnt_tracks = df_for_playlist.shape[0]
    if cnt_tracks > 0:
        playlist = sp.user_playlist_create(
            user.spotify_user_name,
            f"New arrivals {today}",
            public=False,
            collaborative=False,
            description="New arrivals playlist",
        )
        ids_to_add = df_for_playlist["id"].tolist()
        batch_size = 100
        for i in range(0, len(ids_to_add), batch_size):
            sp.playlist_add_items(
                playlist["id"],
                ids_to_add[i : i + batch_size],
                position=i,
            )
        logger.info(f"Playlist created with {cnt_tracks} tracks!")
    else:
        logger.info("No new tracks added today from playlists or artists.")


if __name__ == "__main__":
    setup_logging()

    ################## step 0 ##################
    parser = argparse.ArgumentParser(description="Spotify Discovery Service")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration JSON file",
    )
    parser.add_argument(
        "--database",
        type=str,
        required=True,
        help="Path to the database folder",
    )
    args = parser.parse_args()

    config_path = args.config
    database_folder = args.database

    main(config_path, database_folder)
