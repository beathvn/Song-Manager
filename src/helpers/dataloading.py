# This script holds different functions to load data of different kinds


# system imports
import yaml

# 3rd party imports
import pandas as pd
import spotipy
import xmltodict


def load_yaml(filepath: str):
    with open(filepath, encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def load_dataframe_from_rekordbox_xml(filepath: str) -> pd.DataFrame:
    """
    Loads data from a Rekordbox XML file and returns it as a pandas DataFrame.

    Args:
        filepath (str): The path to the Rekordbox XML file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the Rekordbox XML file.

    Raises:
        ValueError: If the provided file does not have a .xml extension.
    """
    # check if the given filepath is a .xml file
    if not filepath.endswith(".xml"):
        raise ValueError(
            f"Please provide a .xml file. You passed a {filepath[-4:]} file."
        )

    with open(filepath, "r") as xml_file:
        input_data = xmltodict.parse(xml_file.read())

    # converting the needed data into a dataframe
    input_data = input_data["DJ_PLAYLISTS"]["COLLECTION"]["TRACK"]
    return pd.DataFrame(input_data)


def get_dict_from_xml(filepath: str) -> dict:
    """reading and parsing a xml file into a dict

    Args:
        filepath (str): path to the xml file you want to open and convert

    Returns:
        dict: the converted xml file as a dict
    """
    with open(filepath, "r") as xml_file:
        input_data = xmltodict.parse(xml_file.read())
        return input_data


def get_playlist_total_tracks(sp: spotipy.Spotify, username: str, playlist_id: str):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks
