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

Once you have the [initial setup](#initial-setup) done (and hav the project open in devcontainer you can use it like this:)

- **new arrival playlists**: for every script make sure you have the virtual environment activated and you are in the root of the project with the shell.
  - to initialize the database (this needs to be done only once), run `XX` # TODO: create init script
  - to create the new arrival playlists, run

    ```bash
    ./scripts/create_new_arrivals_playlists.sh
    ```

todo # TODO: create the necessary scripts

todo: # TODO: maybe one needs to save a playlist to his profile (using the spotify app) for it to work...
