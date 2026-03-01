cd "$(dirname "$0")/../../.."
source .venv/bin/activate

cd services/spotify_downloader
source env/.env.local

if [ -n "$CLIENT_ID" ] && [ -n "$CLIENT_SECRET" ]; then
    spotdl $SPOTIFY_URL --output $DOWNLOAD_DESTINATION --bitrate 128k --client-id $CLIENT_ID --client-secret $CLIENT_SECRET --no-cache
else
    spotdl $SPOTIFY_URL --output $DOWNLOAD_DESTINATION --bitrate 128k
fi

python src/main.py --config $CONFIG_PATH --playlist-url $SPOTIFY_URL --output-folder $OUTPUT_FOLDER