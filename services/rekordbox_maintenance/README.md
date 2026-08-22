# Rekordbox Maintenance Service

## Summary

This service helps maintain and optimize a Rekordbox library. It remains the
DJ's responsibility to know and manage their library.

It currently exports a sorted track title and artist list as a PDF, Excel workbook, or CSV file. Duplicate `@Location` checking is documented only; `check_for_duplicates.py` is not currently part of this service.

## Export track list

Copy `env/.env.export_track_list.example` to the ignored `env/.env.export_track_list` file, then set `DATABASE_FOLDER` and `OUTPUT_FOLDER`. Double-click `scripts/export_track_list.sh` in Finder, or run it from the repository root:

```bash
./services/rekordbox_maintenance/scripts/export_track_list.sh
```

The launcher defaults to the latest Rekordbox 7 XML snapshot and PDF output. Set `REKORDBOX_VERSION` to a `YYYY-MM-DD` snapshot date and `OUTPUT_FORMAT` to `csv`, `pdf`, or `xlsx` in `env/.env.export_track_list` to override them. You can also run the Python entry point directly after activating the project environment:

```bash
python src/export_track_list.py --database /path/to/xmls --output-folder /path/to/exports --version 2026-08-22 --format csv
```

Supported output formats are `csv`, `pdf`, and `xlsx`; `pdf` is the default. The PDF contains a sorted, paginated table with song name and artist columns.

## Normalize Audio

Normalizing audio using [pydub](https://github.com/jiaaro/pydub).

`normalize_audio.py` selects tracks whose Rekordbox comment contains a keyword
and copies them to a staging folder. Its normalization call is currently
disabled, so it does not yet write normalized audio.

**ATTENTION:** This script converts songs in the .m4a format to the .mp3 format. This is because pydub cannot handle the .m4a files.
Why is that a problem? Because you can have a folder containing both a FILENAME.mp3 and a FILENAME.m4a file, that are actually two totally different songs. If you now use the normalize_audio.py script to normalize the FILENAME.m4a because it is very quiete and put it back in your folder, it will ask you if you want to replace the file, since FILENAME.mp3 already exists. But the FILENAME.mp3 is not the file you want to replace, since it is a totally different song. You need to delete the FILENAME.m4a file in your folder manually, place the newly created and normalized FILENAME.mp3 into the folder and select "keep both". Afterwards, you need to go (again manually - sorry for that) into the xml file of rekordbox and change manually the '@Location' key of the FILENAME.m4a to the new file.

Sadly you cannot use the relocate button in rekordbox, since it lets you only relocate files from the same format.
