# Execute this script to create a playlist with all songs that are 
# newly added (in playlists or favourite artists) since the last time you executed the script.

cd "$(dirname "$0")/.."
source .venv/bin/activate

python src/streaming/dataset.py --mode "update"
python src/streaming/create_new_songs_playlist.py