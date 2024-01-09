# This file contains some utility functions that are used in multiple places in the project.


# system imports
import os
import platform
import subprocess
import sys

# 3rd party imports
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
            

def open_file(filepath: str)-> None:
    """Opens the file specified in filepath. Handles the different platforms (windows, mac...)

    Args:
        filepath (str): path you want to open
    """
    if platform.system() == 'Darwin':
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':
        os.startfile(filepath)
    else:  # linux variants
        subprocess.call(('xdg-open', filepath))


def get_auth_spotipy_obj(config: dict, scope: str) -> spotipy.Spotify:
    """Create spotipy object from given username and environmental
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI
    """
    
    # getting the environmental variables
    client_id = config['client_id']
    client_secret = config['client_secret']
    redirect_uri = config['redirect_uri']
    
    if client_id is None:
        raise Exception('SPOTIPY_CLIENT_ID not provided')
    elif client_secret is None:
        raise Exception('SPOTIPY_CLIENT_SECRET not provided')
    elif redirect_uri is None:
        raise Exception('SPOTIPY_REDIRECT_URI not provided')

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            redirect_uri=config['redirect_uri'],
        ),
    )
    return sp


def read_csv_custom(data_folder: str, filename: str) -> pd.DataFrame:
    """Function to execute the read_csv function from pandas 
    with datetime for the appropriate columns

    Args:
        data_folder (str): folder where the data is stored
        filename (str): file you want to read

    Returns:
        pd.DataFrame: loaded csv file as pandas dataframe
    """
    if filename in ['artists.csv', 'playlists.csv', 'tracks_fav.csv']:
        df = pd.read_csv(os.path.join(data_folder, filename))
        df.date_added = pd.to_datetime(df.date_added).dt.date
        df.date_removed = pd.to_datetime(df.date_removed).dt.date
        return df
    elif filename == 'popularity.csv':
        df = pd.read_csv(os.path.join(data_folder, filename))
        df.date = pd.to_datetime(df.date).dt.date
        return df
    else:
        # no conversion needs to be done
        df = pd.read_csv(os.path.join(data_folder, filename))
        return df
