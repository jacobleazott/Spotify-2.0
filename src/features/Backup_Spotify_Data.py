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
import contextlib
import logging
import sqlite3
from datetime import datetime

import src.General_Spotify_Helpers as gsh

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

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
        col_name = col[1]   # Column name (not really needed for our case)
        col_type = col[2].upper()  # Column type in SQLite schema
        python_type = sqlite_type_mapping.get(col_type, str)  # Default to str if type is not found
        column_types.append(python_type)

    return column_types


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class BackupSpotifyData(LogAllMethods):
    
    def __init__(self, spotify, db_path: str=None, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        self.db_path = db_path or f"{Settings.BACKUPS_LOCATION}{datetime.today().date()}.db"
        
    @contextlib.contextmanager
    def connect_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn 
            conn.commit()
        finally:
            conn.close()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Inserts a variable amount of elements into a database table while verifying the types of your 'values'
                 match that of the columns in your 'table'.
    INPUT: table - What table we will insert into (str).
           values - What data will be inserted into the table.
           batch_size - How many 'values' we can add into a table at once for performance issues.
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""""" 
    def _insert_many(self, table: str, values: Union[list[dict], list[tuple], list], batch_size: int=500) -> None:
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

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Creates the necessary tables for our SQLite db. These include the artist table, playback table, tracks
                 table, and the playlists-tracks many to many relationship table.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _create_backup_data_db(self) -> None:
        with self.connect_db() as db_conn:
            db_conn.executescript("""
                PRAGMA foreign_keys = ON;
                
                CREATE TABLE IF NOT EXISTS playlists (
                    id text UNIQUE PRIMARY KEY,
                    name text,
                    description text
                ) WITHOUT ROWID;

                CREATE TABLE IF NOT EXISTS artists (
                    id text UNIQUE PRIMARY KEY,
                    name text
                ) WITHOUT ROWID;

                CREATE TABLE IF NOT EXISTS albums (
                    id text UNIQUE PRIMARY KEY,
                    name text,
                    release_date text
                ) WITHOUT ROWID;

                CREATE TABLE IF NOT EXISTS tracks (
                    id text UNIQUE PRIMARY KEY,
                    name text,
                    duration_ms integer,
                    is_local integer,
                    is_playable integer
                ) WITHOUT ROWID;

                CREATE TABLE IF NOT EXISTS followed_artists (
                    id text PRIMARY KEY REFERENCES artists(id)
                ) WITHOUT ROWID;

                CREATE TABLE IF NOT EXISTS playlists_tracks (
                    id_playlist text REFERENCES playlists(id),
                    id_track text REFERENCES tracks(id)
                );

                CREATE TABLE IF NOT EXISTS tracks_artists (
                    id_track text REFERENCES tracks(id),
                    id_artist text REFERENCES artists(id),
                    UNIQUE(id_track, id_artist)
                );

                CREATE TABLE IF NOT EXISTS tracks_albums (
                    id_track text REFERENCES tracks(id),
                    id_album text REFERENCES albums(id),
                    UNIQUE(id_track, id_album)
                );

                CREATE TABLE IF NOT EXISTS albums_artists (
                    id_album text REFERENCES albums(id),
                    id_artist text REFERENCES artists(id),
                    UNIQUE(id_album, id_artist)
                );
            """)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Queries all followed artists by the user, inserts them into the database.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    @gsh.scopes(["user-follow-read"])
    def _add_followed_artists_to_db(self) -> None:
        artists = self.spotify.get_user_artists(info=["id", "name"])
        self.logger.info(f"\t Inserting {len(artists)} Artists")
        self._insert_many("artists", artists)
        self._insert_many("followed_artists", [artist['id'] for artist in artists])
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Fills all appropriate tables from the tracks from a given playlist.
    INPUT: playlist_id - Id that we will be using to grab tracks and link together in our db.
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    @gsh.scopes(["playlist-read-private"])
    def _insert_tracks_into_db_from_playlist(self, playlist_id: str) -> None:
        # Regular Object Table Entries
        track_table_entries, album_table_entries, artist_table_entries = [], [], []
        # Many To Many Relationship Tables
        playlists_tracks_entries, tracks_artists_entries, tracks_albums_entries, album_artists_entries = [], [], [], []
        
        tracks = self.spotify.get_playlist_tracks(playlist_id
                                         , track_info=['id', 'name', 'duration_ms', 'is_local', 'is_playable']
                                         , album_info=['id', 'name', 'release_date', 'artists']
                                         , artist_info=['id', 'name'])
        
        self.logger.debug(f"\tTracks #: {len(tracks)}")
        
        for track in tracks:
            if track['is_playable'] is None:
                track['is_playable'] = False
            # Replace any None values with a unique identifier so we have all data
            if track['is_local']:
                track = replace_none(track, f"local_track_{track['name']}")
            
            track_table_entries.append((track['id'], track['name'], track['duration_ms']
                                        , track['is_local'], track['is_playable']))
            album_table_entries.append((track['album']['id'], track['album']['name'], track['album']['release_date']))
            artist_table_entries += [(artist['id'], artist['name']) for artist in track['artists']]
            artist_table_entries += [(artist['id'], artist['name']) for artist in track['album']['artists']]
            playlists_tracks_entries.append((playlist_id, track['id']))
            tracks_artists_entries += [(track['id'], artist['id']) for artist in track['artists']]
            tracks_albums_entries.append((track['id'], track['album']['id']))
            album_artists_entries += [(track['album']['id'], artist['id']) for artist in track['album']['artists']]
            
        self._insert_many("tracks", track_table_entries)
        self._insert_many("albums", album_table_entries)
        self._insert_many("artists", artist_table_entries)
        self._insert_many("playlists_tracks", playlists_tracks_entries)
        self._insert_many("tracks_artists", tracks_artists_entries)
        self._insert_many("tracks_albums", tracks_albums_entries)
        self._insert_many("albums_artists", album_artists_entries)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Adds all user playlists into our database.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    @gsh.scopes(["playlist-read-private"])
    def _add_user_playlists_to_db(self) -> None:
        user_playlists = self.spotify.get_user_playlists(info=["id", "name", "description"])
        self.logger.info(f"\t Inserting {len(user_playlists)} Playlists")
        self._insert_many("playlists", user_playlists)
        
        for playlist in user_playlists:
            self.logger.debug(f"\t Saving Data For Playlist: {playlist['name']}")
            self._insert_tracks_into_db_from_playlist(playlist['id'])
        
        with self.connect_db() as db_conn:
            self.logger.info(f"\t Inserted {db_conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]} Tracks")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Performs a backup of our local spotify library. This includes all of our followed artists and all of
                 our playlists including all track and artist data from anything in those playlists.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""    
    def backup_data(self) -> None:
        self.logger.info(f"CREATING NEW BACKUP =====================================================================")
        self._create_backup_data_db()
        self._add_followed_artists_to_db()
        self._add_user_playlists_to_db()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════