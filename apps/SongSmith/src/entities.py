import os
from datetime import date
from pydantic import BaseModel
import pandas as pd


class Authentication(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    """Spotify API authentication credentials"""


class CatalogItem(BaseModel):
    """this will be used for playlists and artists"""

    id: str
    url: str
    name: str
    allowed_tracks: int
    """how many tracks allowed for the new arrival playlist from this Item"""


class User(BaseModel):
    """Defines the user configuration *(which playlists/artists to consider, username, etc.)*"""

    id: str
    auth: Authentication
    spotify_user_name: str
    playlists: list[CatalogItem]
    artists: list[CatalogItem]

    @property
    def playlists_df(self) -> pd.DataFrame:
        """Convert playlists to DataFrame"""
        return pd.DataFrame([playlist.model_dump() for playlist in self.playlists])

    @property
    def artists_df(self) -> pd.DataFrame:
        """Convert artists to DataFrame"""
        return pd.DataFrame([artist.model_dump() for artist in self.artists])

    @classmethod
    def from_json(cls, json_path: str) -> "User":
        """Load user configuration from JSON file"""
        with open(json_path, "r") as f:
            return cls.model_validate_json(f.read())

    def to_json(self, json_path: str) -> None:
        """Save user configuration to JSON file"""
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            f.write(self.model_dump_json(indent=2))


class Track(BaseModel):
    id: str
    name: str
    artist_ids: list[str]
    artist_names: list[str]
    date_added: date
    added_from: str
    """playlist id, artist id or favorites when added from favorites"""
