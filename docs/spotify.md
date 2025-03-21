# Spotify

This section is all about the spotify functionality of this repo.

- [Spotify](#spotify)
  - [Feature overview](#feature-overview)
  - [Initial setup](#initial-setup)
  - [Usage](#usage)

## Feature overview

- **Creating** a spotify playlist of newly added songs of specified playlists and artists using [spotipy](https://github.com/spotipy-dev/spotipy)
- For **downloading** songs of a whole playlist, use [spotdl](https://github.com/spotDL/spotify-downloader). See below for the cli usage:

    ```bash
    spotdl SPOTIFY_PLAYLIST_URL --output ~/Downloads
    spotdl YOUTUBE_URL|SPOTIFY_URL --output ~/Downloads
    ```

    > [!NOTE]
    > This will download to your local Downloads folder, which is mounted in the devcontainer.

## Initial setup

Before you start, there is a few things you need to setup:

1. Setting up an account in [spotify for developers](https://developer.spotify.com) and create a spotify app.
2. Copy the values for `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` and `SPOTIPY_REDIRECT_URI` once the app is created
3. Create a configuration file (like [this one](../config/connection_dummy.yaml)) and fill it with your credentials.
   > [!CAUTION]
   > Make sure not to commit any sensitive information
4. Create another configuration file where you define the **playlists** and **artists** you want to use. You can use [this one](../config/spotiplaylist_dummy.yaml) as a template (the data folders in the configuration will be used as root for the database necessary).

## Usage

Once you have the [initial setup](#initial-setup) done, the easiest way to use the spotify functionalities is to open the project in a devcontainer in vscode.

For the 'new arrival playlist', you need to initialize the databse (this needs to be done only once). For that run the script XX. # TODO: create init script (need to create csv files, run dataset script in create mode)

todo # TODO: create the necessary scripts

todo: # TODO: maybe one needs to save a playlist to his profile (using the spotify app) for it to work...
