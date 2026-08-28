#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$repository_root"
source .venv/bin/activate

cd services/rekordbox_syncer
environment_file="env/.env.change_location"
if [[ ! -f "$environment_file" ]]; then
    echo "Environment file not found: $environment_file" >&2
    echo "Copy env/.env.change_location.example to $environment_file and configure it first." >&2
    exit 1
fi

source "$environment_file"

if [[ -z "${PATH_TO_RB:-}" || -z "${OLD_LOCATION:-}" || -z "${NEW_LOCATION:-}" || -z "${SAVE_LOCATION:-}" || -z "${LOCATION_OF_INTEREST:-}" ]]; then
    echo "Environment file must set all Rekordbox XML path settings." >&2
    exit 1
fi

python src/change_location.py \
    --path-to-rb "$PATH_TO_RB" \
    --old-location "$OLD_LOCATION" \
    --new-location "$NEW_LOCATION" \
    --save-location "$SAVE_LOCATION" \
    --location-of-interest "$LOCATION_OF_INTEREST"
