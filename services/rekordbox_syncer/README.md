# Rekordbox Sync Service

This service helps you synchronize your entire rekordbox library between multiple laptops. For the metadata, the `.xml` rekordbox file is used.

**Process example:**
1. you work on your main pc, analyze the newest music
2. export the latest `.xml` file
3. sync local pc music folder with an external drive
4. go to second pc and sync music folder with external drive
5. run script to update the location key of the `.xml` file to respect the location of the second pc (otherwise we cannot import the new songs)
6. import the new songs and reanalyze (but only the phrase, because bpm etc. is already there in `.xml` file)

- changing the location of an "old" to a "new location" by overwriting the "@Location" key in the xml file
- Comparing two xml files to find differences, based on some set rules it looks for.

---
**What the scripts do:**
- `change_location.py`: lets you change all the "@Location" information of a rekordbox xml file from an "old location" to a "new location". Why would you need this feature? Imagine, you have an different laptop for your dj sets (2nd laptop) than for the track preparation and stick syncing (1st laptop). The most up-to-date colleciton is found on the 1st laptop. So you can export the rekordbox xml file there and import it in the 2nd laptop. For this import to work, you need the "@Locaiton" key of the songs to be correct, otherwise rekordbox simply tells you that it couldn't import the songs, because they are not found.
- `diff_xml.py`: compares two given xml files ("old" and "new") by looking at specific keys in the xml files. The newly added songs are currently not considered a difference. This script serves the purpose to find the songs the "new" xml file has changed in comparison to the old (such as the rating, grouping, file itself by looking at the filesize and length and more keys). You can configure for which keys the file needs to be delted and reimported (like when you change the audiofile itself), or simply reimported (when the changes are only in the metadata). Note: be sure the @Location base location for the audio files is identical for the two xml files - otherwise, everything is a difference.