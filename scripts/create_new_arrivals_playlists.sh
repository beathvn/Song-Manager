cd "$(dirname "$0")/.."
source .venv/bin/activate

python services/spotify_discovery/src/main.py --config data/config_test.json --database data