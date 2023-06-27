# This script normalizes the audio of all the files inside a given folder and saves the normalized audios to a new folder.
# This new folder must already exist, and you need to pass the path to it via program argument.
# NOTE: m4a songs are converted into mp3 songs, since the algorithm used cannot handle m4a songs.
# under the hood pydub is used


# system imports
from argparse import ArgumentParser
import os
import sys
sys.path.append('../src/')

# 3rd party imports
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.utils import mediainfo
from tqdm import tqdm

# user imports
from logger import logger


def main(args):
    source_folder = args.source
    destination_folder = args.destination

    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f)) and not f.startswith('.')]

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



if __name__ == "__main__":
    logger.info('Start of program: Normalize Audio')

    parser = ArgumentParser()
    parser.add_argument('-s', '--source')
    parser.add_argument('-d', '--destination')

    args = parser.parse_args()
    if os.path.exists(args.source) and os.path.exists(args.destination):
        main(args)
    else:
        raise FileNotFoundError('One of the provided directories does not exist. ' +
                                f'Please create them. You passed: {args.source} and {args.destination}')
    
    logger.info('End of program: Normalize Audio\n')

    #TODO: I want to open the logfile, just if there were warnings