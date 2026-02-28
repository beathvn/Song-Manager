# Spotify Discovery Service

## Summary

The purpose of this service is to discover new tracks on Spotify based on a given and pre-defined search process, which incorporates also user preferences.

Here is what it does right now: create a spotify playlist of newly added songs to specified playlists and artists.
Under the hood, the [spotipy](https://github.com/spotipy-dev/spotipy) library is used.

## Creating the 'New Arrivals' playlist

The playlist is created based on a tracks table, stored as a `.parquet` file with the following schema:
```mermaid
erDiagram
    TRACKS {
        string id
        string name
        list[string] artist_ids
        list[string] artist_names
        datetime date_added
        string added_from
    }
```
With this database, the following process is used to create the 'new tracks' playlist:

1. Update the tracks table with the newest songs:
	1. find the latest favorite tracks and add them
	2. get current state of playlists and artists
	3. add `n` new tracks for playlist and artist to the table, based on user preferences (the `n` most popular ones will be added) - make sure not to add duplicates
2. Create the playlist based on the new tracks added today: only include tracks, that are added from playlists or artists, not from favorites.