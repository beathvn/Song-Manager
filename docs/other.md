# Other

This section covers other functionalities, that are not directly related to spotify or rekordbox.

- [Other](#other)
  - [Normalize Audio](#normalize-audio)
  - [Sync folders](#sync-folders)

## Normalize Audio

Normalizing audio using [pydub](https://github.com/jiaaro/pydub).

Execute the **normalize_audio.py** script to normalize the audio files using pydub (<https://github.com/jiaaro/pydub>) found in folder A and save the normalized audio files in folder B. Both folder A and B are given to the program via program argument.

**ATTENTION:** This script converts songs in the .m4a format to the .mp3 format. This is because pydub cannot handle the .m4a files. Why is that a problem? Because you can have a folder containing both a FILENAME.mp3 and a FILENAME.m4a file, that are actually two totally different songs. If you now use the normalize_audio.py script to normalize the FILENAME.m4a because it is very quiete and put it back in your folder, it will ask you if you want to replace the file, since FILENAME.mp3 already exists. But the FILENAME.mp3 is not the file you want to replace, since it is a totally different song. You need to delete the FILENAME.m4a file in your folder manually, place the newly created and normalized FILENAME.mp3 into the folder and select "keep both". Afterwards, you need to go (again manually - sorry for that) into the xml file of rekordbox and change manually the '@Location' key of the FILENAME.m4a to the new file. Sadly you cannot use the relocate button in rekordbox, since it lets you only relocate files from the same format.

## Sync folders

Synchronizing a slave folder to a master folder.

Simply execute the **sync_folders.py** script with the program arguments you want to have. For more information see the first few rows on the source file.
