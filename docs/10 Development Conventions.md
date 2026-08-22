# Development conventions

## Service-oriented structure

Song-Manager is organized as a set of focused services under `services/`.
Keep behavior that serves one workflow inside its service; do not couple
services through direct imports or machine-specific paths.

```text
services/<service>/
├── src/        # Python entry points and service-specific code
├── scripts/    # Runnable shell launchers
├── env/        # Example environment configuration
├── config/     # Checked-in, non-secret configuration
└── research/   # Exploratory notebooks
```

Reusable Spotify, Rekordbox, and logging functionality belongs in the matching
workspace package under `libs/` (`spotify_client`, `rekordbox_client`, or
`song_common`), rather than being copied between services. Keep user-facing
workflow and status documentation in `docs/`, while service READMEs contain
service-specific setup, commands, and troubleshooting.

## Command-line options

Use kebab-case for public command-line options:

```bash
python src/sync_folders.py --master-folder /source --slave-folder /destination
```

In Python, use the corresponding snake_case attribute. `argparse` maps option
names automatically, so `--master-folder` is available as `args.master_folder`.

```python
parser.add_argument("--master-folder")
sync_folders(args.master_folder, args.slave_folder)
```

Keep Python modules, functions, variables, and shell script filenames in
snake_case. Environment-variable names remain uppercase with underscores, such
as `MASTER_MUSIC_FOLDER`.
