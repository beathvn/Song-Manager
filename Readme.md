# Song-Manager
Important notice: bevore using this project: See **Disclaimer** at the end of this document.

This project provides the following main funcionalities:
1. Downloading songs from a given spotify playlist using ytmdl https://github.com/deepjyoti30/ytmdl
2. Creating a spotify playlist containing newly added songs of specified playlists using spotipy: https://github.com/spotipy-dev/spotipy
3. Synchronizing a slave folder to a master folder.
4. Different functionalities regarding rekordbox xml files including
    1. changing the location of an "old" to a "new location" by overwriting the "@Location" key in the xml file
    2. converting some provided keys from an rekordbox 5 xml file to a rekordbox 6 xml file
    3. Searching for duplicates in the rekordbox xml "@Location" key

## Getting started
Before you start, there is a few things you need to setup:
1. Setting up a spotify developer account and a spotify app.
2. Adding your SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and the SPOTIPY_REDIRECT_URI (you get those, once you finished step 1) to the environmental variables.
3. Setting up some yaml files for configuration. Threwout the project yaml files should be passed as a program argument to configure the different runs. I suggest you create a config folder holding all your different yaml files. Since you should place your username and other personal information inside the yaml file, i made git, ignore the "config" folder.

## Usage:
### Song downloading
For Song downloading use the scripts **download_songs.py** or **download_songs_from_url.py**. For more information on how to run these scripts and what they do, see the first lines of the source code. There you can find a description.

### Spotify Playlist Creation
* The playlists are created on the base of csv files. So before you execute the **create_new_songs_playlist.py** file, execute the **create_csv_files.py** script, which creates .csv files and saves it to the data folder you specified. There are 3 csv files created:
1. *YYYY-MM-DD-ART.csv*: ART stands for artist and this csv file holds the popular songs of in the config file specified artists.
3. *YYYY-MM-DD-PLA.csv*: PLA stands for playlists and this csv file holds all the songs of in the config file specified playlists.
2. *YYYY-MM-DD-FAV.csv*: FAV stands for favourites and this csv file holds all the hearted songs of the user.

* Once you have the new csv files inside your specified data folder, execute the **create_new_songs_playlist.py**, which creates a spotify playlist with all the newly songs added. The following process defines the "newly added songs":
1. Compare the current csv files to the previous ones and creating a table with all songs, that are only present in the newest csv files (ART and PLA).
2. Removing songs, that are already saved using the FAV csv file.
3. Applying limits to each playlist so that there are not added too many songs. The limits are specified in the config file of the program. If there are 10 new songs found in a playlist, but the limit is set to 6, the 6 most popular songs are added. The popularity information provided by spotify is used. The popularity index is calculated by the total streams of a song, how recently a song has been played and the frequency a song has been played.
4. Creating the playlist with the remaining songs.

### Sync folders
Simply execute the **sync_folders.py** script with the program arguments you want to have. For more information see the first few rows on the source file.

### Rekordbox
* The **change_location.py** script lets you change all the "@Location" information of a rekordbox xml file from an "old location" to a "new location". Why would you need this feature: Imagine, you have an different laptop for your dj sets (2nd laptop) than for the track preparation and stick syncing (1st laptop). The most up-to-date colleciton is found on the 1st laptop. So you can export the rekordbox xml file there and import it in the 2nd laptop. For this import to work, you need the "@Locaiton" key of the songs to be correct, otherwise rekordbox simply tells you that it couldn't import the songs, because they are not found.
* The **convert_rb5_to_rb6.py** script lets you update some defined keys in a rekordbox 6 xml file on the base of the rekordbox 5 xml file. The script uses the classes defined in **RB_handler.py** script under the hood, to perform the conversion.
* The **check_for_duplicates.py** script searches the "@Location" key of a rekordbox xml file to find duplicates.

# Disclaimer
This project is provided "as is", without express or implied warranties of any kind. The author assumes no responsibility or liability for the use of this project or for the accuracy, reliability, or timeliness of the information contained herein. Any actions taken based on this project or the information provided therein are done so at the user's own risk.

This project is for entertainment purposes only. The author assumes no liability for any violations of copyright, laws or regulations resulting from the use of this project. It is the user's responsibility to ensure that their actions are in accordance with applicable law.

It is strongly recommended that users purchase their favorite songs and music content legally in order to properly support artists and rights holders. Any use of this project to illegally distribute, reproduce or access copyrighted material without authorization is expressly prohibited.

By using this project, the user agrees to hold the author harmless from any claims, damages or legal consequences that may arise from the use of this project.
