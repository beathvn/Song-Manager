# Rekordbox Maintenance Service

## Summary

This service contains Rekordbox maintenance commands and research notebooks. The DJ remains responsible for reviewing and managing the library.

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

## Data quality research

Copy `env/.env.data_quality.example` to the ignored `env/.env.data_quality` file, then set `DATABASE_FOLDER` to the folder containing the Rekordbox XML exports. Open `research/20_rekordbox_data_quality_review.ipynb` from its `research/` directory and run its cells in order.

## Normalize audio research

Copy `env/.env.normalize_audio.example` to the ignored `env/.env.normalize_audio` file and configure it before opening `research/30_normalize_audio.ipynb`.

**Attention:** The experiment converts `.m4a` files to `.mp3`. A pre-existing MP3 with the same filename can be a different song, so replacement must be reviewed manually. After choosing the correct output file, update the corresponding Rekordbox XML `@Location` manually; Rekordbox cannot relocate files across formats.
