cd "$(dirname "$0")/../../.."
source .venv/bin/activate

cd services/rekordbox_syncer
source env/.env.harddrive.example

python src/sync_folders.py --master-folder "$MASTER_MUSIC_FOLDER" --slave-folder "$SLAVE_MUSIC_FOLDER"
python src/sync_folders.py --master-folder "$MASTER_XML_FOLDER" --slave-folder "$SLAVE_XML_FOLDER"
