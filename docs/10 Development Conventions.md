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

## Markdown prose

Write prose as one physical line per paragraph. Start a new paragraph when introducing a distinct concept or topic. Do not add soft line breaks solely to wrap text at a fixed line length.

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

## Finder launchers and local environment files

Shell launchers intended to be started by double-clicking in Finder must not require command-line arguments. They may intentionally load a fixed ignored environment file from their own `env/` directory; this makes the Finder workflow reliable because no terminal argument can be supplied. Each service README must name its fixed local environment file and the matching tracked example file, when one exists.

## Optional root-level launcher links

For convenient Finder access, create a symbolic link in the ignored repository-root `scripts/` directory that points to a service launcher. Run this command from the repository root, choosing the target service script and shortcut name:

```bash
ln -s "$(pwd)/services/rekordbox_maintenance/scripts/export_track_list.sh" scripts/export_track_list.sh
```

The link is a local convenience and is not versioned because its absolute target path is machine-specific. Keep the real launcher in its service's `scripts/` directory; update or recreate the link when that launcher is renamed.
