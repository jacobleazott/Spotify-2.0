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
import logging
import sqlite3
from datetime import datetime

import General_Spotify_Helpers as gsh
from decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
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
        if len(values) > 0:
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
    def create_backup_data_db(self) -> None:
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS playlists (
                                id text UNIQUE PRIMARY KEY,
                                name text,
                                description text
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS artists (
                                id text UNIQUE PRIMARY KEY,
                                name text
                                ) WITHOUT ROWID; """)
        
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS albums (
                                id text UNIQUE PRIMARY KEY,
                                name text,
                                release_date text
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS tracks(
                                id text UNIQUE PRIMARY KEY,
                                name text,
                                duration_ms integer,
                                is_local integer,
                                is_playable integer
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS followed_artists(
                                id text PRIMARY KEY REFERENCES artists(id)
                                ) WITHOUT ROWID; """)

        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS playlists_tracks(
                                id_playlist text REFERENCES playlists(id),
                                id_track text REFERENCES tracks(id)
                                )""")
        
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS tracks_artists(
                                id_track text REFERENCES tracks(id),
                                id_artist text REFERENCES artists(id)
                                )""")
        
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS tracks_albums(
                                id_track text REFERENCES tracks(id),
                                id_album text REFERENCES albums(id)
                                )""")
        
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS albums_artists(
                                id_album text REFERENCES albums(id),
                                id_artist text REFERENCES artists(id)
                                )""")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Queries all followed artists by the user, inserts them into the database.
    INPUT: NA
    Output: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_followed_artists_to_db(self) -> None:
        artists = self.spotify.get_user_artists(info=["id"])
        self.logger.info(f"\t Inserting {len(artists)} Artists")
        self.insert_many("followed_artists", artists)
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION:
    INPUT: 
    Output: 
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def insert_tracks_into_db_from_playlist(self, playlist_id: str) -> None:
        # Regular Object Table Entries
        track_table_entries, album_table_entries, artist_table_entries = [], [], []
        # Many To Many Relationship Tables
        playlists_tracks_entries, tracks_artists_entries, tracks_albums_entries, album_artists_entries = [], [], [], []
        
        tracks = self.spotify.get_playlist_tracks(playlist_id
                                         , track_info=['id', 'name', 'duration_ms', 'is_local', 'preview_url']
                                         , album_info=['id', 'name', 'release_date', 'artists']
                                         , artist_info=['id', 'name'])
        
        for track in tracks:
            track_table_entries.append((track['id'], track['name'], track['duration_ms'], track['is_local'], 
                                        track['preview_url'] is not None))
            album_table_entries.append((track['album_id'], track['album_name'], track['album_release_date']))
            artist_table_entries += [(artist['id'], artist['name']) for artist in track['artists']]
            artist_table_entries += [(artist['id'], artist['name']) for artist in track['album_artists']]
            playlists_tracks_entries.append((playlist_id, track['id']))
            tracks_artists_entries += [(track['id'], artist['id']) for artist in track['artists']]
            tracks_albums_entries.append((track['id'], track['album_id']))
            album_artists_entries += [(track['album_id'], artist['id']) for artist in track['album_artists']]
            
        self.insert_many("tracks", track_table_entries)
        self.insert_many("albums", album_table_entries)
        self.insert_many("artists", artist_table_entries)
        self.insert_many("playlists_tracks", playlists_tracks_entries)
        self.insert_many("tracks_artists", tracks_artists_entries)
        self.insert_many("tracks_albums", tracks_albums_entries)
        self.insert_many("albums_artists", album_artists_entries)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION:
    INPUT: 
    Output: 
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_user_playlists_to_db(self) -> None:
        user_playlists = self.spotify.get_user_playlists(info=["id", "name", "description"])
        self.logger.info(f"\t Inserting {len(user_playlists)} Playlists")
        self.insert_many("playlists", user_playlists)
        
        for playlist in user_playlists:
            self.logger.debug(f"\t Saving Data For Playlist: {playlist['name']}")
            self.insert_tracks_into_db_from_playlist(playlist['id'])
            
        self.logger.info(f"\t Inserted {self.db_conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]} Tracks")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: 
    INPUT: 
    Output: 
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""    
    def backup_data(self) -> None:
        self.db_conn = sqlite3.connect(f"databases/backups/{datetime.today().date()}.db")
        self.logger.info(f"CREATING NEW BACKUP =====================================================================")
        with self.db_conn:
            self.create_backup_data_db()
            self.add_followed_artists_to_db()
            self.add_user_playlists_to_db()
        
        self.db_conn.commit()
        self.db_conn.close()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════