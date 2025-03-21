# Rekordbox

This section is all about the [rekordbox](https://rekordbox.com/) functionality of this repo.

Working with the `.xml` export of your rekordbox library. These are the **features**:

- [Rekordbox](#rekordbox)
  - [Feature overview](#feature-overview)
  - [Scripts and what they do](#scripts-and-what-they-do)

## Feature overview

- changing the location of an "old" to a "new location" by overwriting the "@Location" key in the xml file
- converting some provided keys from an rekordbox 5 xml file to a rekordbox 6 xml file
- Searching for duplicates in the rekordbox xml "@Location" key
- Comparing two xml files to find differences, based on some set rules it looks for.

## Scripts and what they do

- [change_location.py](../src/collection/change_location.py): lets you change all the "@Location" information of a rekordbox xml file from an "old location" to a "new location". Why would you need this feature? Imagine, you have an different laptop for your dj sets (2nd laptop) than for the track preparation and stick syncing (1st laptop). The most up-to-date colleciton is found on the 1st laptop. So you can export the rekordbox xml file there and import it in the 2nd laptop. For this import to work, you need the "@Locaiton" key of the songs to be correct, otherwise rekordbox simply tells you that it couldn't import the songs, because they are not found.
- [convert_rb5_to_rb6.py](../src/collection/convert_rb5_to_rb6.py): lets you update some defined keys in a rekordbox 6 xml file on the base of the rekordbox 5 xml file. The script uses the classes defined in [RB_handler.py](../src/helpers/RB_handler.py) script under the hood, to perform the conversion.
- [check_for_duplicates.py](../src/collection/check_for_duplicates.py): searches the "@Location" key of a rekordbox xml file to find duplicates.
- [diff_xml.py](../src/collection/diff_xml.py): compares two given xml files ("old" and "new") by looking at specific keys in the xml files. The newly added songs are currently not considered a difference. This script serves the purpose to find the songs the "new" xml file has changed in comparison to the old (such as the rating, grouping, file itself by looking at the filesize and length and more keys). You can configure for which keys the file needs to be delted and reimported (like when you change the audiofile itself), or simply reimported (when the changes are only in the metadata). Note: be sure the @Location base location for the audio files is identical for the two xml files - otherwise, everything is a difference.
