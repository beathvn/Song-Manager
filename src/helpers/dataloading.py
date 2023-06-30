# This script holds different functions to load data of different kinds


# system imports
import os
import yaml

# 3rd party imports
import pandas as pd
import spotipy
import xmltodict

# user imports
import helpers.dataprocessing as dataprocessing


def load_yaml(filepath: str):
    with open(filepath) as file:
        config = yaml.safe_load(file)
    return config


def load_dataframe_from_rekordbox_xml(filepath: str)-> pd.DataFrame:
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
    if not filepath.endswith('.xml'):
        raise ValueError(
            f'Please provide a .xml file. You passed a {filepath[-4:]} file.')

    with open(filepath, 'r') as xml_file:
        input_data = xmltodict.parse(xml_file.read())

    # converting the needed data into a dataframe
    input_data = input_data['DJ_PLAYLISTS']['COLLECTION']['TRACK']
    return pd.DataFrame(input_data)


def get_dict_from_xml(filepath: str) -> dict:
    """reading and parsing a xml file into a dict

        Args:
            filepath (str): path to the xml file you want to open and convert

        Returns:
            dict: the converted xml file as a dict
        """
    with open(filepath, 'r') as xml_file:
        input_data = xmltodict.parse(xml_file.read())
        return input_data


def get_playlist_total_tracks(sp: spotipy.Spotify, username: str, playlist_id: str):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def get_txt_lines_as_list(filepath: str)-> list:
    """Reads the given .txt file in filepath and returns a list, 
    where each entry is a seperate line in the txt file. Removes illegal characters.

    Args:
        filepath (str): path to the .txt file you want to read

    Returns:
        list: holding the lines of the .txt file
    """
    my_file = open(filepath, "r")
    data = my_file.read()

    if data == '':
        return []
    
    # removing the characters ytmdl cannot handle
    data = dataprocessing.remove_illegal_characters(data)

    # replacing end of line('/n') with ' ' and
    # splitting the text it further when '.' is seen.
    data = data.split("\n")

    # now return the list, but remove empty entries
    return list(filter(bool, data))



def get_dataframes_from_folder(data_path: str)-> list:
    """Creates 3 dataframes for the last 2 playlist data and the last favourite data.
    Make sure the data_path holds the data in .csv format and the favourite data is stored with a FAV in it

    Args:
        data_path (str): path to folder, where the .csv files are stored

    Returns:
        list: 3 dataframes in the order [df_playlists_old, df_playlists_new, df_fav]
    """
    
    # getting the files
    files = [os.path.join(data_path, i) for i in os.listdir(data_path) if i.endswith('.csv') and not i.startswith('.')]

    # splitting in fav files and playlist files
    pla_files = [x for x in files if 'PLA' in x]
    fav_files = [x for x in files if 'FAV' in x]
    art_files = [x for x in files if 'ART' in x]

    pla_files.sort()
    fav_files.sort()
    art_files.sort()

    # combining the two dataframes and dropping the duplicates

    # reading the playlist dataframes
    df_pla_old = pd.read_csv(pla_files[-2])
    df_pla_new = pd.read_csv(pla_files[-1])

    # reading the followed artists dataframes
    df_art_old = pd.read_csv(art_files[-2])
    df_art_new = pd.read_csv(art_files[-1])

    # reading favs corresponding to the playlist_new
    df_fav = pd.read_csv(fav_files[-1])

    return [df_pla_old, df_pla_new, df_art_old, df_art_new, df_fav]