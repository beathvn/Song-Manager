# Spotify Downloader Service

this service helps you download tracks from Spotify by saving information of the playlist downloaded to a CSV file. The download process itself can done with spotdl cli tool.

NOTE: when you are getting a timeout error with spotdl, try using one of your own spotify applications. For that, you need to clear the spotdl cache with `rm -rf ~/.spotdl/.spotipy` and then call it with these parameters:

- `--client-id CLIENT_ID`
- `--client-secret CLIENT_SECRET`
- `--no-cache`

For more details, see [docs spoti](../../docs/spotify.md)
