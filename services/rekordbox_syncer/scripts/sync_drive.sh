#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path-to-local-profile>" >&2
    exit 2
fi

profile_path="$1"
if [[ ! -f "$profile_path" ]]; then
    echo "Profile not found: $profile_path" >&2
    echo "Copy env/.env.sync.example to an ignored local file first." >&2
    exit 1
fi

profile_path="$(cd "$(dirname "$profile_path")" && pwd)/$(basename "$profile_path")"
repository_root="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$repository_root"
source .venv/bin/activate

cd services/rekordbox_syncer
source "$profile_path"

python src/sync_folders.py \
    --master-folder "$MASTER_MUSIC_FOLDER" \
    --slave-folder "$SLAVE_MUSIC_FOLDER"
python src/sync_folders.py \
    --master-folder "$MASTER_XML_FOLDER" \
    --slave-folder "$SLAVE_XML_FOLDER"
