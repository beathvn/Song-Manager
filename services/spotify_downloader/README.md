# Spotify Downloader Service

## Summary

this service helps you download tracks from Spotify by saving information of a playlist to a `.csv` file.

> [!NOTE] download in CLI
> The download process itself is done with the spotdl cli tool - not in the the python scripts

## SpotDL usage

For **downloading** songs of a whole playlist, use [spotdl](https://github.com/spotDL/spotify-downloader). See below for the cli usage (more information in [spotdl usage docs](https://spotdl.github.io/spotify-downloader/usage/)):

```bash
spotdl "SPOTIFY_PLAYLIST_URL" --output ~/Downloads
spotdl download "YOUTUBE_URL|SPOTIFY_URL" --output ~/Downloads
```

## Troubleshooting

when you are getting a timeout error with spotdl, try using one of your own spotify applications. For that, you need to clear the spotdl cache with `rm -rf ~/.spotdl/.spotipy` and then call it with these parameters:

- `--client-id CLIENT_ID`
- `--client-secret CLIENT_SECRET`
- `--no-cache`

the script already implements the logic for it - just make sure the set the dedicated environment variables (otherwise leave them empty) - see the example env file for help.