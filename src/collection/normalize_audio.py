# This script normalizes the audio of all the files inside a given folder and saves the normalized audios to a new folder.
# This new folder must already exist, and you need to pass the path to it via program argument.
# NOTE: m4a songs are converted into mp3 songs, since the algorithm used cannot handle m4a songs.
# under the hood pydub is used


# system imports
from argparse import ArgumentParser
import os
import shutil
import sys
sys.path.append('../src/')

# 3rd party imports
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.utils import mediainfo
from tqdm import tqdm
import pandas as pd

# user imports
from helpers.logger import logger
import helpers.dataloading as dataloading


def copy_leise_songs_to_directory(xml_file: str, destination_folder: str, keyword: str):
    logger.info(f'Searcihng the {xml_file} for songs with the keyword {keyword}.')
    data_dict = dataloading.get_dict_from_xml(xml_file)
    data = pd.DataFrame(data_dict['DJ_PLAYLISTS']['COLLECTION']['TRACK'])

    location_series = data[data['@Comments'].str.contains(keyword, case=False)]['@Location']
    location_list = location_series.apply(lambda x: x[16:].replace('%20', ' ').replace(
        '%26', '&').replace('%27', '\'').replace('%c3%ab', 'ë').replace('%5b', '[').replace('%5d', ']').replace('%c3%b6', 'ö').replace('%c3%bc', 'ü')).to_list()
    
    logger.info(f'Found {len(location_list)} songs that have the keyword leise in it.')
    logger.info(f'Copy those songs to {destination_folder}.')

    for file in tqdm(location_list):
        shutil.copy(file, destination_folder)

    return
    

def normalize_files(files: list, source_folder, destination_folder):

    for file in tqdm(files, desc='Normalizing Audio', unit='song'):
        # Load the audio file
        audio = AudioSegment.from_file(os.path.join(source_folder, file))

        # Normalize the audio without clipping
        normalized_audio = normalize(audio, headroom=0)

        current_bitrate = mediainfo(os.path.join(source_folder, files[1]))['bit_rate']
        curr_format = file[-3:]
        
        # ffmpeg not compatible with m4a... converting it to mp3
        if curr_format == 'm4a':
            logger.warning(f'Converted {file} from m4a to mp3 format!')
            curr_format = 'mp3'
            file = file[:-3] + 'mp3'

        # Export the normalized audio
        normalized_audio.export(os.path.join(destination_folder, file),
                                format=curr_format, bitrate=current_bitrate)


def main(args):
    logger.info('Start of program: normalize_audio.py...')
    source_folder = args.source
    destination_folder = args.destination
    xml_file = args.xmlfile

    if not os.path.exists(args.source):
        os.mkdir(args.source)
    else:
        logger.warning(f'Folder {source_folder} already exists. Aborting...')
        raise FileExistsError(f'Folder {source_folder} already exists. Aborting...')
    if not os.path.exists(args.destination):
        os.mkdir(args.destination)
    else:
        logger.warning(f'Folder {destination_folder} already exists. Aborting...')
        raise FileExistsError(f'Folder {destination_folder} already exists. Aborting...')
    
    # copy files into a new folder
    copy_leise_songs_to_directory(xml_file, source_folder, 'leise')

    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f)) and not f.startswith('.')]
    # normalize_files(files, source_folder, destination_folder)

    logger.info('Start of program: normalize_audio.py\n')


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-s', '--source')
    parser.add_argument('-d', '--destination')
    parser.add_argument('-x', '--xmlfile')

    args = parser.parse_args()

    main(args)

    #TODO: I want to open the logfile, just if there were warnings