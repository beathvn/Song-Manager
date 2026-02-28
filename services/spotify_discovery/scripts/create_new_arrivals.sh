cd "$(dirname "$0")/../../.."
source .venv/bin/activate

cd services/spotify_discovery
source env/.env.local
python src/main.py --config $CONFIG_PATH --database $TRACKS_DATABASE_FOLDER