import os
import pandas as pd


class DatabaseHandler:
    def __init__(self, data_folder: str):
        self.data_folder = data_folder

        table_names = {
            "tracks": ["id", "name", "artists"],
            "tracks_fav": ["id", "date_added", "date_removed"],
            "popularity": ["id", "date", "value"],
            "playlists": ["id", "track_id", "date_added", "date_removed"],
            "playlists_names": ["id", "name"],
            "artists": ["id", "track_id", "date_added", "date_removed"],
            "artists_names": ["id", "name"],
        }

        def create_table(table_name, columns):
            outpath = os.path.join(self.data_folder, f"{table_name}.csv")
            pd.DataFrame(columns=columns).to_csv(outpath, index=False)

        for table in table_names:
            if not os.path.exists(os.path.join(self.data_folder, f"{table}.csv")):
                create_table(table)
