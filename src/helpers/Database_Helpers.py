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


SCHEMA_FIELDS = {
    "playlists": {
         "id" : "TEXT UNIQUE PRIMARY KEY"
        , "name"         : "TEXT"
        , "description"  : "TEXT"
        , "__without_rowid__" : True
    },
    "artists": {
         "id" : "TEXT UNIQUE PRIMARY KEY"
        , "name"         : "TEXT"
        , "__without_rowid__" : True
    },
    "albums": {
         "id" : "TEXT UNIQUE PRIMARY KEY"
        , "name"         : "TEXT"
        , "release_date" : "TEXT"
        , "total_tracks" : "INTEGER"
        , "__without_rowid__" : True
    },
    "tracks": {
         "id" : "TEXT UNIQUE PRIMARY KEY"
        , "name"         : "TEXT"
        , "duration_ms"  : "INTEGER"
        , "is_local"     : "INTEGER"
        , "is_playable"  : "INTEGER"
        , "disc_number"  : "INTEGER"
        , "track_number" : "INTEGER"
        , "__without_rowid__" : True
    },
    "followed_artists": {
         "id" : "TEXT PRIMARY KEY REFERENCES artists(id)"
        , "__without_rowid__" : True
    },
    "playlists_tracks": {
         "id_playlist"  : "TEXT REFERENCES playlists(id)"
        , "id_track"     : "TEXT REFERENCES tracks(id)"
    },
    "tracks_artists": {
         "id_track"     : "TEXT REFERENCES tracks(id)"
        , "id_artist"    : "TEXT REFERENCES artists(id)"
        , "__constraints__" : ["UNIQUE(id_track, id_artist)"]
    },
    "tracks_albums": {
         "id_track"     : "TEXT REFERENCES tracks(id)"
        , "id_album"     : "TEXT REFERENCES albums(id)"
        , "__constraints__" : ["UNIQUE(id_track, id_album)"]
    },
    "albums_artists": {
         "id_album"     : "TEXT REFERENCES albums(id)"
        , "id_artist"    : "TEXT REFERENCES artists(id)"
        , "__constraints__" : ["UNIQUE(id_album, id_artist)"]
    },
    "listening_session": {
         "time"         : "TIMESTAMP NOT NULL"
        , "id_track"     : "TEXT REFERENCES tracks(id)"
    },
    "track_play_counts": {
         "id_track"     : "TEXT REFERENCES tracks(id) PRIMARY KEY"
        , "play_count"   : "INTEGER NOT NULL"
        , "__without_rowid__" : True
    },
}

def extract_values(item: dict, table: str) -> tuple:
    return tuple(item.get(field) for field in get_table_fields(table))

def get_table_fields(table: str) -> list[str]:
    return [field for field in SCHEMA_FIELDS[table] if not field.startswith("__")]

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
    
    def __init__(self, db_path: str=Settings.LISTENING_VAULT_DB,
                 schema: DatabaseSchema=DatabaseSchema.FULL,
                 logger: logging.Logger=None) -> None:
        self.db_path = db_path
        self.schema = schema
        self.logger = logger if logger is not None else logging.getLogger()
        self.create_database()
        
    @contextlib.contextmanager
    def connect_db(self):
        print(self.db_path)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn 
            conn.commit()
        finally:
            conn.close()
            
    def create_database(self) -> None:
        schema_sql = []

        for table, fields in SCHEMA_FIELDS.items():
            if self.schema == DatabaseSchema.SNAPSHOT and table in {"listening_session", "track_play_counts"}:
                continue
            
            field_copy = fields.copy()
            stmt = self._generate_create_statement(table, field_copy)
            schema_sql.append(stmt)
            
        with self.connect_db() as db_conn:
            db_conn.executescript("\n".join(schema_sql))
            
    def _generate_create_statement(self, table: str, fields: dict[str, str]) -> str:
        constraints = fields.pop("__constraints__", [])
        without_rowid = fields.pop("__without_rowid__", False)
        columns = ",\n\t".join(f"{name} {col_type}" for name, col_type in fields.items())

        constraints_clause = ""
        if constraints:
            constraints_clause = ",\n\t" + ",\n\t".join(constraints)

        statement = f"CREATE TABLE IF NOT EXISTS {table} (\n    {columns}{constraints_clause}\n)"
        if without_rowid:
            statement += " WITHOUT ROWID"

        return statement + ";"
    
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
    
    def id_is_in_db(self, id: str, table: str) -> bool:
        with self.backup_db_conn as db_conn:
            return db_conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id)).fetchone() is not None
        
    
    def print_playlist_tracks(self, playlist_id: str) -> None:
        query = """
            SELECT 
                t.id AS track_id,
                t.name AS track_name,
                t.duration_ms,
                t.is_local,
                t.is_playable,
                t.disc_number,
                t.track_number,
                GROUP_CONCAT(DISTINCT ar.name) AS artists,
                al.name AS album_name,
                al.release_date,
                al.total_tracks
            FROM playlists_tracks pt
            JOIN tracks t ON pt.id_track = t.id
            LEFT JOIN tracks_artists ta ON t.id = ta.id_track
            LEFT JOIN artists ar ON ta.id_artist = ar.id
            LEFT JOIN tracks_albums tal ON t.id = tal.id_track
            LEFT JOIN albums al ON tal.id_album = al.id
            WHERE pt.id_playlist = ?
            GROUP BY t.id
            ORDER BY t.disc_number, t.track_number;
        """

        with self.connect_db() as db_conn:
            cursor = db_conn.execute(query, (playlist_id,))
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]

            if not rows:
                print(f"No tracks found for playlist ID '{playlist_id}'.")
                return

            # Print headers
            print("\n" + "-" * 80)
            print("TRACKS IN PLAYLIST".center(80))
            print("-" * 80)
            print(" | ".join(col_names))
            print("-" * 80)

            # Print rows
            for row in rows:
                print(" | ".join(str(item) if item is not None else "" for item in row))
            print("-" * 80)
            
    def print_tracks_by_id(self, track_ids: list[str]) -> None:
        if not track_ids:
            print("No track IDs provided.")
            return

        placeholders = ", ".join("?" for _ in track_ids)
        query = f"""
            SELECT 
                t.id AS track_id,
                t.name AS track_name,
                t.duration_ms,
                t.is_local,
                t.is_playable,
                t.disc_number,
                t.track_number,
                GROUP_CONCAT(DISTINCT ar.name) AS artists,
                al.name AS album_name,
                al.release_date,
                al.total_tracks
            FROM tracks t
            LEFT JOIN tracks_artists ta ON t.id = ta.id_track
            LEFT JOIN artists ar ON ta.id_artist = ar.id
            LEFT JOIN tracks_albums tal ON t.id = tal.id_track
            LEFT JOIN albums al ON tal.id_album = al.id
            WHERE t.id IN ({placeholders})
            GROUP BY t.id
            ORDER BY t.disc_number, t.track_number
        """

        with self.connect_db() as db_conn:
            cursor = db_conn.execute(query, track_ids)
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]

            if not rows:
                print("No matching tracks found.")
                return

            print("\n" + "-" * 80)
            print("TRACK INFO".center(80))
            print("-" * 80)
            print(" | ".join(col_names))
            print("-" * 80)

            for row in rows:
                print(" | ".join(str(val) if val is not None else "" for val in row))
            print("-" * 80)


    

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════