#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../.."
source .venv/bin/activate

cd services/rekordbox_syncer
source env/.env.change_location.example

python src/change_location.py \
    --path-to-rb "$PATH_TO_RB" \
    --old-location "$OLD_LOCATION" \
    --new-location "$NEW_LOCATION" \
    --save-location "$SAVE_LOCATION" \
    --location-of-interest "$LOCATION_OF_INTEREST"
