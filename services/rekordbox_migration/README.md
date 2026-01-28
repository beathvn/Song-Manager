# Rekordbox migration service

helping you migrate data from older rekordbox versions to newer ones based on the `.xml` export of your library.

converting some provided keys from an rekordbox 5 xml file to a rekordbox 6 xml file

- `convert_rb5_to_rb6.py`: lets you update some defined keys in a rekordbox 6 xml file on the base of the rekordbox 5 xml file. The script uses the classes defined in [RB_handler.py](../src/helpers/RB_handler.py) script under the hood, to perform the conversion.