# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIFY BACKUP                            CREATED: 2020-6-13          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This script simply takes all of the users current followed artists and playlists and backs them up to an SQLite DB.
#   It utilizes a simple many to many relationship table for playlists and tracks.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import sqlite3
import logging
from datetime import datetime

from decorators import *
import General_Spotify_Helpers as gsh

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class BackupSpotifyData(LogAllMethods):
    FEATURE_SCOPES = ["user-follow-read"
                    , "playlist-read-private"]
    db_conn = None
    
    def __init__(self, spotify, logger=None):
        self.spotify = spotify
        self.spotify.scopes = self.FEATURE_SCOPES
        self.logger = logger if logger is not None else logging.getLogger()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Queries user for a valid artist id.
    INPUT: table - what table we will insert into (str).
           values - what data will be inserted into the table (list).
    Output: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def insert_many(self, table: str, values: list) -> None:
        placeholders = "?, " * len(values[0])
        query = "INSERT OR IGNORE INTO %s VALUES (%s)" % (table, placeholders[:-2])
        data = [tuple(d.values()) for d in values] if type(values[0]) is dict else values
        self.db_conn.executemany(query, data)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Creates the necessary tables for our SQLite db. These include the artist table, playback table, tracks
                 table, and the playlists-tracks many to many relationship table.
    INPUT: NA
    Output: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def create_backup_data_db(self):
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS playlists (
                                id text UNIQUE PRIMARY KEY,
                                name text
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS tracks(
                                id text UNIQUE PRIMARY KEY,
                                name text,
                                duration_ms integer,
                                is_local integer,
                                album_id text,
                                album_name text,
                                release_date text,
                                artist_id text,
                                artist_name text
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS followed_artists(
                                id text UNIQUE PRIMARY KEY,
                                name text
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS playlists_tracks(
                                id_playlist text REFERENCES playlists(id),
                                id_track text REFERENCES tracks(id)
                                )""")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Queries all followed artists by the user, inserts them into the database.
    INPUT: NA
    Output: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_followed_artists_to_db(self):
        artists = self.spotify.get_user_artists(info=["id", "name"])
        self.logger.info(f"\t Inserting {len(artists)} Artists")
        self.insert_many("followed_artists", artists)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Gathers all users playlists, gets all the tracks from said playlists. Creates a many to many
                 relationship between all tracks and all playlists.
    INPUT: NA
    Output: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_playlists_to_db(self):
        playlists = self.spotify.get_user_playlists(info=["id", "name"])
        self.logger.info(f"\t Inserting {len(playlists)} Playlists")
        self.insert_many("playlists", playlists)
        for playlist in playlists:
            self.logger.debug(f"\t Saving Data For Playlist: {playlist['name']}")
            tracks = self.spotify.get_playlist_tracks(playlist["id"]
                                                     , track_info=["id", "name", "duration_ms", "is_local"]
                                                     , album_info=["id", "name", "release_date"]
                                                     , artist_info=["id", "name"])
            if len(tracks) == 0:
                self.logger.debug(f"\t SKIPPING Empty Playlist: {playlist['name']}")
                continue

            tracks_ready_for_insert = []
            for track in tracks:
                tmp_val = []
                for key, value in track.items():
                    if type(value) is list:
                        value = value[0]
                    if type(value) is dict:
                        for key2, value2 in value.items():
                            tmp_val.append(value2)
                    else:
                        tmp_val.append(value)
                tracks_ready_for_insert.append(tuple(tmp_val))

            track_id_map = [(playlist["id"], x[0])for x in tracks_ready_for_insert]
            
            self.insert_many("tracks", tracks_ready_for_insert)
            self.insert_many("playlists_tracks", track_id_map)
        
        self.logger.info(f"\t Inserted {self.db_conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]} Tracks")
        
    def backup_data(self):
        self.db_conn = sqlite3.connect(f"databases/backups/{datetime.today().date()}.db")
        self.logger.info(f"CREATING NEW BACKUP =====================================================================")
        with self.db_conn:
            self.create_backup_data_db()
            self.add_followed_artists_to_db()
            self.add_playlists_to_db()
        
        self.db_conn.commit()
        self.db_conn.close()
        
        
def main():
    spotify = gsh.GeneralSpotifyHelpers()
    backup = BackupSpotifyData(spotify)
    backup.backup_data()


if __name__ == "__main__":
    main()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════