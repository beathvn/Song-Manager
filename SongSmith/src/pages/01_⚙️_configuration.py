# system imports
from datetime import datetime
import math

# 3rd party imports
import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Callable

# user imports
from entities import User, Track, Authentication, CatalogItem

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
    stops when there is an error
    """
    try:
        sp = _get_spotify_obj(user, "user-library-read")
        playlist = sp.playlist(playlist_url)
        return playlist["id"], playlist["name"]
    except Exception as e:
        st.error(f"Error fetching playlist: {e}")
        st.stop()


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


def _autopopulate_table(
    df: pd.DataFrame,
    item_type: str,
    get_id_name_fn: Callable[[User, str], tuple[str, str]],
    user: User,
    editor_key: str,
    auto_state: str,
    key_delta: int,
):
    if df.isnull().values.any():
        if df["allowed_tracks"].isnull().any() or df["url"].isnull().any():
            st.toast("can just autopopulate **name** and **id**", icon="⚠️")
        else:
            pb = st.progress(0)
            total = len(df[df["id"].isnull() | df["name"].isnull()])
            count = 0
            for idx, row in df.iterrows():
                if pd.isna(row["id"]) or pd.isna(row["name"]):
                    _id, _name = get_id_name_fn(user, row["url"])
                    df.at[idx, "id"] = _id
                    df.at[idx, "name"] = _name
                    count += 1
                    pb.progress(count / total)
            pb.empty()
            st.session_state[editor_key] += key_delta
            st.session_state[auto_state] = df
            st.rerun()
    else:
        st.toast(f"No null values in the {item_type} table.", icon="⚠️")


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

if "tracks" not in st.session_state:
    st.session_state.tracks = None

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
    st.session_state.artists_autopopulated = None

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
st.markdown(
    ":orange-badge[:warning: Note] Don't add playlists that are curated by spotify - they won't work."
)
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
    _autopopulate_table(
        df_playlists_edited,
        "playlist",
        get_playlist_id_name,
        user,
        "playlist_editor_key",
        "playlists_autopopulated",
        1,
    )

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
    _autopopulate_table(
        df_artists_edited,
        "artist",
        get_artist_id_name,
        user,
        "artist_editor_key",
        "artists_autopopulated",
        -1,
    )

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

disable_init_tracks = (
    client_id == ""
    or client_secret == ""
    or redirect_uri == ""
    or spotify_user_name == ""
)

if st.button(
    "Init tracks table",
    use_container_width=True,
    help="This will create a new tracks table based on your favorites - disabled on missing infos",
    disabled=disable_init_tracks,
):
    sp = _get_spotify_obj(user, "user-library-read")
    total_tracks = sp.current_user_saved_tracks(limit=1, offset=0)["total"]

    # 50 is the max amount you can fetch in a single request
    request_limit = 50
    iterations = math.ceil(total_tracks / request_limit)

    results = []

    pb = st.progress(0, "Fetching your saved tracks...")
    for curr_iteration in range(iterations):
        track_results = sp.current_user_saved_tracks(
            limit=request_limit, offset=curr_iteration * request_limit
        )
        results += track_results["items"]
        pb.progress((curr_iteration + 1) / iterations, "Fetching your saved tracks...")

    pb.empty()

    tracks_list = [
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
    ]

    df = pd.DataFrame([vars(track) for track in tracks_list])
    st.session_state.tracks = df
    st.toast("Tracks table created successfully!", icon="✅")

if st.session_state.tracks is not None:
    df_tracks = st.session_state.tracks
    st.dataframe(
        df_tracks,
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "⬇️ Download tracks table",
        df_tracks.to_parquet(index=False),
        file_name=f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tracks.parquet",
        mime="application/parquet",
        help="This will download the current tracks table as a parquet file.",
        use_container_width=True,
        type="primary",
    )
