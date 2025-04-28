# Song Smith

Welcome to Song Smith. This is a simple web application that can be deployed to the cloud.

## How it works

When executed, we want to generate a playlist of songs that arrived newly in the playlists/artists the user chose to follow. For that to work, we create a Tracks table, that contains all tracks, that have been shown to the user in the past. This is how it works:

1. Update the Tracks table to hold all the user favorite tracks *(set added_from = 'favorites')*
2. list tracks in the playlist/artist
3. Drop tracks, that are already in the Tracks table (maybe not just using the track id, but also track name, artists, since in spotify sometimes one song is uploaded multiple times)
4. Sort the tracks by popularity
5. Keep the first n tracks, where n is the number of allowed tracks by the user for that playlist/artist
6. Write those track_ids to the Tracks table and populate the Tracks table with all the necessary information (track name, artists, etc.) - set the date_added to the current date and the added_from to the playlist/artist
7. Continue with the next playlist/artist and repeat the process

Once the Tracks table is up-to-date, follow these steps to generate a playlist:

1. Drop favorites
2. Keep only the tracks that have been added in the current date
3. create the playlist

> [!NOTE]
> Initialize the Tracks table with the favorite tracks of the user.
