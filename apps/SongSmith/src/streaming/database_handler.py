import os
import pandas as pd
from entities import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def _get_spotify_obj(user: User, scop: str) -> spotipy.Spotify:
    """Get the Spotify object with the given scope"""
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scop,
            **user.auth.model_dump(),
        ),
    )

class DatabaseHandler:
    def __init__(self, user: User):
        self.user = user
        self.sp: spotipy.Spotify = _get_spotify_obj(user, "user-library-read")