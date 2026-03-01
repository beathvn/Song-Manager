cd "$(dirname "$0")/../../.."
source .venv/bin/activate

cd services/rekordbox_maintenance
source env/.env.local

python src/export_tracknames_excel.py --database $DATABASE_FOLDER --output-folder $OUTPUT_FOLDER