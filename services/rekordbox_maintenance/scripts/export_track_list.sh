#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$repository_root"
source .venv/bin/activate

cd services/rekordbox_maintenance
environment_file="env/.env.export_track_list"
if [[ ! -f "$environment_file" ]]; then
    echo "Environment file not found: $environment_file" >&2
    echo "Create it with DATABASE_FOLDER and OUTPUT_FOLDER before running this script." >&2
    exit 1
fi

source "$environment_file"

if [[ -z "${DATABASE_FOLDER:-}" || -z "${OUTPUT_FOLDER:-}" ]]; then
    echo "Environment file must set DATABASE_FOLDER and OUTPUT_FOLDER." >&2
    exit 1
fi

python src/export_track_list.py \
    --database "$DATABASE_FOLDER" \
    --output-folder "$OUTPUT_FOLDER" \
    --version "${REKORDBOX_VERSION:-latest}" \
    --format "${OUTPUT_FORMAT:-pdf}"
