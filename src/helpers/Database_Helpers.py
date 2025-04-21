# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    DATABASE SPOTIFY HELPERS                 CREATED: 2024-10-03          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Querying Spotify for thousands of tracks, hundreds of playlists, hundreds of artists is a very costly execution. To
#   mitigate this expensive operation we can use our local backup database instead for a lot of different features. I 
#   envision this one day being wrapped up with GSH so that if you need a playlist that isn't available in the local db
#   it could then automatically go grab it from spotify. However, for now we will restrict these features to just our 
#   local db. This just means features like Shuffle won't work on brand new playlists or include added tracks until 2AM
#   everyday.
# 
# One important aspect is that we continue to return data in a dictionary format just like GSH. This way we can easily
#   drop this in wherever we want and it should just work. This is a design constraint I should be more strict about
#   over the entire project, never just packing values into tuples and assuming everyone knows the order. That way if 
#   we run into a scenario where we need 'name' and it isn't in the dictionary our exception is helpful and we can
#   trace back instead of just seeing that track[9] is out of range.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import contextlib
import logging
import os
import sqlite3

from enum import Enum
from glob import glob

from src.helpers.decorators import *
from src.helpers.Settings   import Settings


class DatabaseSchema(Enum):
    FULL = "full"         # includes listening_session and track_play_counts
    SNAPSHOT = "snapshot" # excludes those two tables
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Finds the given types of an SQLite table columns and returns their associated python type to help us
             verify data going into our DB.
INPUT: db_conn - SQLite DB connection that we will grab our 'table' columns from.
       table - SQLite table that we will grab column types of.
OUTPUT: List of python types 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_column_types(db_conn, table: str) -> list:
    with db_conn:
        columns = db_conn.execute(f"PRAGMA table_info({table})").fetchall()

    sqlite_type_mapping = {
        'INTEGER': int,
        'TEXT': str,
        'REAL': float,
        'BLOB': bytes,
        'NUMERIC': float  # NUMERIC 'could' be an int, we don't use it anyways 
    }

    column_types = []
    for col in columns:
        col_type = col[2].upper()  # Column type in SQLite schema
        python_type = sqlite_type_mapping.get(col_type, str)  # Default to str if type is not found
        column_types.append(python_type)

    return column_types


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Collection of methods similar to GSH that grab from our latest local backup rather than spotify itself.
             Table definitions can be found in Backup_Spotify_Data.py.
             The Database we use is just the latest from our Backup_Spotify_Data location.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class DatabaseHelpers(LogAllMethods):
    
    def __init__(self, db_path: str = Settings.LISTENING_VAULT_DB,
                 schema: DatabaseSchema = DatabaseSchema.FULL,
                 logger: logging.Logger=None) -> None:
        self.db_path = db_path
        self.schema = schema
        self.logger = logger if logger is not None else logging.getLogger()
        self.create_database()
        
    @contextlib.contextmanager
    def connect_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn 
            conn.commit()
        finally:
            conn.close()
            
    def create_database(self) -> None:
        with self.connect_db() as db_conn:
            db_conn.executescript(self._get_schema_script())
        
    def _get_schema_script(self) -> str:
        common_tables = """
            CREATE TABLE IF NOT EXISTS playlists (
                id TEXT UNIQUE PRIMARY KEY,
                name TEXT,
                description TEXT
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS artists (
                id TEXT UNIQUE PRIMARY KEY,
                name TEXT
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS albums (
                id TEXT UNIQUE PRIMARY KEY,
                name TEXT,
                release_date TEXT
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT UNIQUE PRIMARY KEY,
                name TEXT,
                duration_ms INTEGER,
                is_local INTEGER,
                is_playable INTEGER
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS followed_artists (
                id TEXT PRIMARY KEY REFERENCES artists(id)
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS playlists_tracks (
                id_playlist TEXT REFERENCES playlists(id),
                id_track TEXT REFERENCES tracks(id)
            );

            CREATE TABLE IF NOT EXISTS tracks_artists (
                id_track TEXT REFERENCES tracks(id),
                id_artist TEXT REFERENCES artists(id),
                UNIQUE(id_track, id_artist)
            );

            CREATE TABLE IF NOT EXISTS tracks_albums (
                id_track TEXT REFERENCES tracks(id),
                id_album TEXT REFERENCES albums(id),
                UNIQUE(id_track, id_album)
            );

            CREATE TABLE IF NOT EXISTS albums_artists (
                id_album TEXT REFERENCES albums(id),
                id_artist TEXT REFERENCES artists(id),
                UNIQUE(id_album, id_artist)
            );
        """

        full_only_tables = """
            CREATE TABLE IF NOT EXISTS listening_session (
                time TIMESTAMP NOT NULL,
                id_track TEXT REFERENCES tracks(id)
            ) WITHOUT ROWID;

            CREATE TABLE IF NOT EXISTS track_play_counts (
                id_track TEXT REFERENCES tracks(id),
                play_count INTEGER NOT NULL
            ) WITHOUT ROWID;
        """

        if self.schema == DatabaseSchema.FULL:
            return full_only_tables + common_tables
        
        return common_tables
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Inserts a variable amount of elements into a database table while verifying the types of your 'values'
                 match that of the columns in your 'table'.
    INPUT: table - What table we will insert into (str).
           values - What data will be inserted into the table.
           batch_size - How many 'values' we can add into a table at once for performance issues.
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""""" 
    def insert_many(self, table: str, values: Union[list[dict], list[tuple], list], batch_size: int=500) -> None:
        if not values:
            return  # No data to insert

        with self.connect_db() as db_conn:
            expected_types = get_column_types(db_conn, table)
        
        # Translates values into our format from either dict, list of tuples, or just list
        data = [tuple(d.values()) for d in values] if type(values[0]) is dict \
                else [(v,) for v in values] if type(values[0]) is not tuple else values 

        for row in data:
            for i, (val, expected_type) in enumerate(zip(row, expected_types)):
                if not isinstance(val, expected_type):
                    raise ValueError(f"'{val}' in column {i+1} of table '{table}' should be of type {expected_type}")

        placeholders = ", ".join("?" for _ in data[0])
        query = f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})"

        with self.connect_db() as db_conn:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                db_conn.executemany(query, batch)
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Since we want to return dicts and not lists of our db data we can use this method to grab our db 
                 column names and zip it up into a dictionary for us.
    INPUT: query - Sqlite query we will fetchall results from and turn into a dict.
    OUTPUT: List of dicts from the db query.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _conn_query_to_dict(self, query: str, p_val: tuple=()) -> list[dict]:
        cursor = self.backup_db_conn.execute(query, p_val)
        column_names = [desc[0] for desc in cursor.description]
        
        return [dict(zip(column_names, row)) for row in cursor.fetchall()]

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs the tracks from a playlist if we have it in our backup database.
    INPUT: playlist_id - Id of playlist we will be grabbing tracks from.
    OUTPUT: List of track dicts.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def db_get_tracks_from_playlist(self, playlist_id: str) -> list[dict]:
        query = f"""
            SELECT tracks.*
            FROM tracks
            JOIN playlists_tracks ON tracks.id = playlists_tracks.id_track
            WHERE playlists_tracks.id_playlist = ?
        """
        return self._conn_query_to_dict(query, p_val=(playlist_id,))

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs all of the artists from our db for a given 'track_id'.
    INPUT: track_id - Id of the track we will be grabbing artists for.
    OUTPUT: List of artist dicts.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def db_get_track_artists(self, track_id: str) -> list[dict]:
        query = f"""
            SELECT artists.* 
            FROM artists
            JOIN tracks_artists ON artists.id = tracks_artists.id_artist
            WHERE tracks_artists.id_track = ?
        """
        return self._conn_query_to_dict(query, p_val=(track_id,))
   
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs all of the playlists in our db.
    INPUT: N/A
    OUTPUT: List of playlist dicts.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""" 
    def db_get_user_playlists(self) -> list[dict]:
        query = f"""
            SELECT playlists.*
            FROM playlists
        """
        return self._conn_query_to_dict(query)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs all of our followed artists from our db.
    INPUT: N/A
    OUTPUT: List of artist dicts.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""" 
    def db_get_user_followed_artists(self) -> list[dict]:
        query = f"""
            SELECT artists.*
            FROM followed_artists
            JOIN artists on artists.id = followed_artists.id 
        """
        return self._conn_query_to_dict(query)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════