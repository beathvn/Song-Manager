# Rekordbox Syncer Service

This service distributes a primary Rekordbox library to a secondary library and
helps refresh existing secondary-library entries from the primary XML. See the
[project overview](../../docs/00%20Overview.md) for the complete workflow.

## Commands

- `scripts/sync_drive.sh <profile>` mirrors music and XML folders using a
  local, ignored profile file. Copy `env/.env.sync.example` to create a profile
  for each destination and direction.
- `src/sync_folders.py` performs one folder mirror. It requires existing source
  and destination folders and removes destination files absent from the source.
- `scripts/change_location.sh <profile>` rewrites XML track paths using a local,
  ignored profile. Copy `env/.env.change_location.example` to create one.
- `src/change_location.py` performs the XML path rewrite and creates the output
  XML file.
- `src/plan_secondary_library_refresh.py --config <path>` compares primary and
  secondary XML snapshots and reports configured metadata changes and obsolete
  secondary entries for manual action in the secondary library; it never
  modifies the primary library. Copy
  `config/secondary_library_refresh.example.yaml` to the ignored
  `config/secondary_library_refresh.yaml` to create the local configuration.

> [!WARNING]
> Do not add `@PlayCount` to the refresh comparison fields. Reimporting a track
> into the secondary library can overwrite a newer DJ play-count value there.
> Primary-library DJ play-count correction is planned as a separate workflow.

Run the shell launchers from the repository root, or activate the project
environment before calling a Python entry point directly:

```bash
source .venv/bin/activate
```
