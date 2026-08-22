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

## Normalize audio research

Audio normalization is currently explored only in `research/30_normalize_audio.ipynb`; there is no supported Python command or Finder launcher. Copy `env/.env.normalize_audio.example` to the ignored `env/.env.normalize_audio` file and configure it before opening the notebook. The notebook contains local-path experiments that select tracks marked as quiet, copy them to a staging folder, and normalize the staged files with [pydub](https://github.com/jiaaro/pydub).

**Attention:** The experiment converts `.m4a` files to `.mp3`. A pre-existing MP3 with the same filename can be a different song, so replacement must be reviewed manually. After choosing the correct output file, update the corresponding Rekordbox XML `@Location` manually; Rekordbox cannot relocate files across formats.
