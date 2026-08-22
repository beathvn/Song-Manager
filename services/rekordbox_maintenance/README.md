# Rekordbox Maintenance Service

## Summary

This service helps maintain and optimize a Rekordbox library. It remains the
DJ's responsibility to know and manage their library.

It currently exports a sorted Excel list of track titles and artists. Duplicate
`@Location` checking is documented only; `check_for_duplicates.py` is not
currently part of this service.

## Normalize Audio

Normalizing audio using [pydub](https://github.com/jiaaro/pydub).

`normalize_audio.py` selects tracks whose Rekordbox comment contains a keyword
and copies them to a staging folder. Its normalization call is currently
disabled, so it does not yet write normalized audio.

**ATTENTION:** This script converts songs in the .m4a format to the .mp3 format. This is because pydub cannot handle the .m4a files.
Why is that a problem? Because you can have a folder containing both a FILENAME.mp3 and a FILENAME.m4a file, that are actually two totally different songs. If you now use the normalize_audio.py script to normalize the FILENAME.m4a because it is very quiete and put it back in your folder, it will ask you if you want to replace the file, since FILENAME.mp3 already exists. But the FILENAME.mp3 is not the file you want to replace, since it is a totally different song. You need to delete the FILENAME.m4a file in your folder manually, place the newly created and normalized FILENAME.mp3 into the folder and select "keep both". Afterwards, you need to go (again manually - sorry for that) into the xml file of rekordbox and change manually the '@Location' key of the FILENAME.m4a to the new file.

Sadly you cannot use the relocate button in rekordbox, since it lets you only relocate files from the same format.
