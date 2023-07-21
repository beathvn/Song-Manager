# This file contains some utility functions that are used in multiple places in the project.


# system imports
import os
import platform
import subprocess
import sys

# 3rd party imports
import spotipy
import spotipy.util as util


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


def get_auth_spotipy_obj(username):
    """Create spotipy object from given username and environmental
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI
    """
    
    # getting the environmental variables
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
    
    if client_id is None:
        raise Exception('SPOTIPY_CLIENT_ID environmental variable not found')
    elif client_secret is None:
        raise Exception('SPOTIPY_CLIENT_SECRET environmental variable not found')
    elif redirect_uri is None:
        raise Exception('SPOTIPY_REDIRECT_URI environmental variable not found')

    token = util.prompt_for_user_token(
            username=username,
            scope='playlist-modify-public',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)
