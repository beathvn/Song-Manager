#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$repository_root"
source .venv/bin/activate

cd services/rekordbox_syncer
environment_file="env/.env.drive"
if [[ ! -f "$environment_file" ]]; then
    echo "Environment file not found: $environment_file" >&2
    echo "Copy env/.env.sync.example to $environment_file and configure it first." >&2
    exit 1
fi

source "$environment_file"

if [[ -z "${MASTER_MUSIC_FOLDER:-}" || -z "${SLAVE_MUSIC_FOLDER:-}" || -z "${MASTER_XML_FOLDER:-}" || -z "${SLAVE_XML_FOLDER:-}" ]]; then
    echo "Environment file must set all music and XML source and destination folders." >&2
    exit 1
fi

python src/sync_folders.py \
    --master-folder "$MASTER_MUSIC_FOLDER" \
    --slave-folder "$SLAVE_MUSIC_FOLDER"
python src/sync_folders.py \
    --master-folder "$MASTER_XML_FOLDER" \
    --slave-folder "$SLAVE_XML_FOLDER"
