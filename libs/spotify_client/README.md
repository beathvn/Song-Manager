# Spotify Client

This library provides an interface to interact with the Spotify Web API (through the `spotipy` package) and manage configuration data needed for the downstream services.

> [!NOTE] getting callout after change of app
> if you still get timeout responses after you have inserted the correct `client_id` and `client_secret`, check if the connection is maybe cached - check for a `.cache` file holding a token
