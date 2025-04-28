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
import sqlite3
from enum import Enum

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

class DatabaseSchema(Enum):
    FULL = "full"         # includes listening_sessions and track_play_counts
    SNAPSHOT = "snapshot" # excludes those two tables


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
    "listening_sessions": {
          "time"         : "TIMESTAMP NOT NULL"
        , "id_track"     : "TEXT REFERENCES tracks(id)"
    },
    "track_play_counts": {
          "id_track"     : "TEXT REFERENCES tracks(id) PRIMARY KEY"
        , "play_count"   : "INTEGER NOT NULL"
        , "__without_rowid__" : True
    },
}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Grabs the column names of an SQLite table from our schema.
INPUT: table - SQLite table that we will grab column names of from SCHEMA_FIELDS.
OUTPUT: List of column names from SCHEMA_FIELDS.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_table_fields(table: str) -> list[str]:
    return [field for field in SCHEMA_FIELDS[table] if not field.startswith("__")]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Finds the given types of an SQLite table columns and returns their associated python type to help us
             verify data going into our DB.
INPUT: tracks - List of tracks we are pulling data from to generate our values to be inserted into the DB.
       playlist_id - Optional playlist ID that we are inserting into.
OUTPUT: Dict of tables and values to insert for the given tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def build_entries_from_tracks(tracks: list, playlist_id: Optional[str]=None) -> dict:
    # Helper function to extract values from a dict for a given table.
    def extract_values(item: dict, table: str) -> tuple:
        return tuple(item.get(field) for field in get_table_fields(table))
    
    # Regular Object Table Entries
    track_table_entries, album_table_entries, artist_table_entries = [], [], []
    # Many To Many Relationship Tables
    playlists_tracks_entries, tracks_artists_entries, tracks_albums_entries, albums_artists_entries = [], [], [], []

    for track in tracks:
        if track['is_playable'] is None:
            track['is_playable'] = False
        if track['album']['total_tracks'] is None:
            track['album']['total_tracks'] = 0

        # Replace any None values with a unique identifier for local tracks
        if track['is_local']:
            track = replace_none(track, f"local_track_{track['name']}")

        track_table_entries.append(extract_values(track, 'tracks'))
        album_table_entries.append(extract_values(track['album'], 'albums'))
        artist_table_entries += [extract_values(artist, 'artists') for artist in track['artists']]
        artist_table_entries += [extract_values(artist, 'artists') for artist in track['album']['artists']]
        
        tracks_artists_entries += [(track['id'], artist['id']) for artist in track['artists']]
        tracks_albums_entries.append((track['id'], track['album']['id']))
        albums_artists_entries += [(track['album']['id'], artist['id']) for artist in track['album']['artists']]
        
        # Add to playlists_tracks if playlist_id is provided
        if playlist_id:
            playlists_tracks_entries.append((playlist_id, track['id']))

    return {
        "tracks": track_table_entries,
        "albums": album_table_entries,
        "artists": artist_table_entries,
        "playlists_tracks": playlists_tracks_entries,
        "tracks_artists": tracks_artists_entries,
        "tracks_albums": tracks_albums_entries,
        "albums_artists": albums_artists_entries
    }


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
DESCRIPTION: This function recursively traverses any list/ dict with any complexity to find and replace every 'None'
             value in it with our 'replace_with' value.
INPUT: data - Any list, value, or dict collection with any complexity that we will be finding 'None' values in.
OUTPUT: 'data' but with any 'None' value replaced with the value of 'replace_with'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def replace_none(data, replace_with: str):
    if isinstance(data, dict):
        # Iterate through dict and recursively go through items
        return {key: replace_none(value, replace_with) for key, value in data.items()}
    elif isinstance(data, list):
        # # Iterate through list and recursively go through elements
        return [replace_none(item, replace_with) for item in data]
    elif data is None:
        # Replace None with the specified string
        return replace_with
    else:
        # Return the value if it's not None, dict, or list
        return data


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
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Context manager for our database connection to enforce foreign key and auto commit.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""         
    @contextlib.contextmanager
    def connect_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn 
            if conn.in_transaction:
                conn.commit()
        finally:
            conn.close()
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Context manager for our database connection in readonly mode.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""         
    @contextlib.contextmanager
    def connect_db_readonly(self):
        uri = f'file:{self.db_path}?mode=ro'
        conn = sqlite3.connect(uri, uri=True)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
        finally:
            conn.close()
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Creates our database with the necessary schema.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""         
    def create_database(self) -> None:
        schema_sql = []

        for table, fields in SCHEMA_FIELDS.items():
            if self.schema == DatabaseSchema.SNAPSHOT and table in {"listening_sessions", "track_play_counts"}:
                continue
            
            field_copy = fields.copy()
            stmt = self._generate_create_statement(table, field_copy)
            schema_sql.append(stmt)
            
        with self.connect_db() as db_conn:
            db_conn.executescript("\n".join(schema_sql))
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Generic function to create a sql statement to create a table.
    INPUT: table - table value we are creating.
           fields - fields that our table will have.
    Output: SQL statement to create our table with name 'table' and columns 'fields'.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""         
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
        with self.connect_db_readonly() as db_conn:
            cursor = db_conn.execute(query, p_val)
            column_names = [desc[0] for desc in cursor.description]
            results = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        
        return results

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
    
    def get_tracks_listened_in_date_range(self, start_date: str, end_date: str) -> list[dict]:
        query = f"""
            SELECT id_track, COUNT(*) as track_count
            FROM listening_sessions
            WHERE time BETWEEN ? AND ?
            GROUP BY id_track;
        """
        return self._conn_query_to_dict(query, p_val=(start_date.strftime("%Y-%m-%d %H:%M:%S")
                                                    , end_date.strftime("%Y-%m-%d %H:%M:%S")))
        
    def get_artists_listened_in_date_range(self, start_date: str, end_date: str) -> list[dict]:
        query = f"""
            SELECT a.*, COUNT(*) AS artist_count
            FROM listening_sessions ls
            JOIN tracks_artists ta ON ls.id_track = ta.id_track
            JOIN artists a ON ta.id_artist = a.id
            WHERE ls.time BETWEEN ? AND ?
            GROUP BY a.name
            ORDER BY artist_count DESC;
        """
        return self._conn_query_to_dict(query, p_val=(start_date.strftime("%Y-%m-%d %H:%M:%S")
                                                    , end_date.strftime("%Y-%m-%d %H:%M:%S")))
        
    def get_artists_appear_in_playlist(self, playlist_id: str) -> list[dict]:
        query = f"""
            SELECT ta.id_artist, a.*, COUNT(*) AS num_appearances
            FROM playlists_tracks pt
            JOIN tracks_artists ta ON pt.id_track = ta.id_track
            JOIN artists a ON ta.id_artist = a.id
            WHERE pt.id_playlist = ?
            GROUP BY ta.id_artist, a.name
            ORDER BY num_appearances DESC;
        """
        return self._conn_query_to_dict(query, p_val=(playlist_id,))
    
    def get_artist_appears_with(self, artist_id: str) -> list[dict]:
        query = f"""
            SELECT DISTINCT a2.*
            FROM tracks_artists ta1
            JOIN tracks_artists ta2 ON ta1.id_track = ta2.id_track
            JOIN artists a2 ON ta2.id_artist = a2.id
            WHERE ta1.id_artist = ? AND ta1.id_artist != ta2.id_artist;
        """
        return self._conn_query_to_dict(query, p_val=(artist_id,))
    
    def get_artist_tracks(self, artist_id: str) -> list[dict]:
        query = f"""
            SELECT t.*
            FROM tracks_artists ta
            JOIN tracks t ON ta.id_track = t.id
            WHERE ta.id_artist = ?;
        """
        return self._conn_query_to_dict(query, p_val=(artist_id,))
        



# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════