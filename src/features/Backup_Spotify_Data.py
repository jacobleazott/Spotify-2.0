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
import re

import src.General_Spotify_Helpers as gsh

from src.helpers.Database_Helpers   import DatabaseHelpers, DatabaseSchema, SCHEMA_FIELDS, extract_values, get_table_fields
from src.helpers.decorators         import *
from src.helpers.Settings           import Settings


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
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class BackupSpotifyData(LogAllMethods):
    
    def __init__(self, spotify, backup_db_path: str=None, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        self.vault_db = DatabaseHelpers(logger=self.logger)
        
        snapshot_db_path = backup_db_path or f"{Settings.BACKUPS_LOCATION}playlist_snapshot_{datetime.today().date()}.db"
        self.snapshot_db = DatabaseHelpers(db_path=snapshot_db_path, schema=DatabaseSchema.SNAPSHOT
                                           , logger=self.logger)
       
    def _clear_vault_playlists(self) -> None:
        self.logger.info(f"\t Clearing Vault Playlists")
        
        with self.vault_db.connect_db() as db_conn:
            db_conn.execute("DELETE FROM playlists_tracks;")
            db_conn.execute("DELETE FROM playlists;")
            db_conn.execute("DELETE FROM followed_artists;")
    
    def _insert_into_databases(self, table: str, values: Union[list[dict], list[tuple], list]) -> None:
        self.vault_db.insert_many(table, values)
        self.snapshot_db.insert_many(table, values)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Queries all followed artists by the user, inserts them into the database.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    @gsh.scopes(["user-follow-read"])
    def _add_followed_artists_to_db(self) -> None:
        artists = self.spotify.get_user_artists(info=["id", "name"])
        self.logger.info(f"\t Inserting {len(artists)} Artists")
        self._insert_into_databases("artists", artists)
        self._insert_into_databases("followed_artists", [artist['id'] for artist in artists])
        
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
                                                , track_info=get_table_fields('tracks')
                                                , album_info=get_table_fields('albums')
                                                , artist_info=get_table_fields('artists'))
        
        self.logger.debug(f"\tTracks #: {len(tracks)}")
        
        for track in tracks:
            if track['is_playable'] is None:
                track['is_playable'] = False
            if track['album']['total_tracks'] is None:
                track['album']['total_tracks'] = 0
            # Replace any None values with a unique identifier so we have all data
            if track['is_local']:
                track = replace_none(track, f"local_track_{track['name']}")
            
            track_table_entries.append(extract_values(track, DatabaseSchema.TRACKS))
            album_table_entries.append(extract_values(track['album'], DatabaseSchema.ALBUMS))
            artist_table_entries += [extract_values(artist, DatabaseSchema.ARTISTS) for artist in track['artists']]
            artist_table_entries += [extract_values(artist, DatabaseSchema.ARTISTS) for artist in track['album']['artists']]
            playlists_tracks_entries.append((playlist_id, track['id']))
            tracks_artists_entries += [(track['id'], artist['id']) for artist in track['artists']]
            tracks_albums_entries.append((track['id'], track['album']['id']))
            album_artists_entries += [(track['album']['id'], artist['id']) for artist in track['album']['artists']]
            
        self._insert_into_databases("tracks", track_table_entries)
        self._insert_into_databases("albums", album_table_entries)
        self._insert_into_databases("artists", artist_table_entries)
        self._insert_into_databases("playlists_tracks", playlists_tracks_entries)
        self._insert_into_databases("tracks_artists", tracks_artists_entries)
        self._insert_into_databases("tracks_albums", tracks_albums_entries)
        self._insert_into_databases("albums_artists", album_artists_entries)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Adds all user playlists into our database.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    @gsh.scopes(["playlist-read-private"])
    def _add_user_playlists_to_db(self) -> None:
        user_playlists = self.spotify.get_user_playlists(info=get_table_fields('playlists'))
        self.logger.info(f"\t Inserting {len(user_playlists)} Playlists")
        self._insert_into_databases("playlists", user_playlists)
        
        for playlist in user_playlists:
            self.logger.debug(f"\t Saving Data For Playlist: {playlist['name']}")
            self._insert_tracks_into_db_from_playlist(playlist['id'])
        
        # TODO: Figure out what stat we want to actually print here now.
        # with self.connect_db() as db_conn:
        #     self.logger.info(f"\t Inserted {db_conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]} Tracks")
    
    def get_all_unique_track_ids(self) -> set[str]:
        listening_data_db = DatabaseHelpers(db_path=Settings.LISTENING_DB, logger=self.logger)
        with listening_data_db.connect_db() as db_conn:
            cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]

            # Filter only tables that are valid years (e.g., "2023", "2024")
            year_tables = [t for t in all_tables if t.isdigit() and len(t) == 4]
            print(year_tables)

            unique_ids = set()

            for table in year_tables:
                query = f"SELECT DISTINCT track_id FROM '{table}'"
                cursor = db_conn.execute(query)
                track_ids = {row[0] for row in cursor.fetchall()}
                unique_ids.update(track_ids)

            return unique_ids


    def verify_tracks_from_listening_data(self) -> None:
        ids = self.get_all_unique_track_ids()
        
        with self.vault_db.connect_db() as db_conn:
            cursor = db_conn.execute("SELECT id FROM tracks")
            vault_ids = {row[0] for row in cursor.fetchall()}
        
        print(len(vault_ids))
        print(len(ids))
        
        missing_ids = ids.difference(vault_ids)
        

        pattern = re.compile(r"^[A-Za-z0-9]{22}$")

        valid_ids = [id for id in missing_ids if pattern.match(id)]
        print(len(valid_ids))
        test_tracks = ['4F2WiwhXDMO1RvhIsp6SBR', '2sV8XYqzsxCLY4djFVlQS8']
        tracks = self.spotify.get_several_tracks(test_tracks, info=["id", "name", "duration_ms", "is_local", "is_playable", "disc_number", "track_number"])
        print(tracks)
        
        # https://open.spotify.com/track/0iDlZGhqZQO1j7Vnmnu8P9?si=bbe8461da04a404a
        
        
        # print("Grabbing tracks")
        # tracks = self.spotify.get_several_tracks(valid_ids
        #              , info=["id", "name", "duration_ms", "is_local", "is_playable", "disc_number", "track_number"])
        
        print("Grabbed all tracks")
        track_table_entries = []
        for track in tracks:
            if track['is_local']:
                track = replace_none(track, f"local_track_{track['name']}")
            print("TRACK", track)
            track_table_entries.append((track['id'], track['name'], track['duration_ms'], track['is_local']
                                        , track['is_playable'], track['disc_number'], track['track_number']))
        
        print("TRACK ENTRIES", track_table_entries)
        self.vault_db.insert_many('tracks', track_table_entries)
        self.vault_db.print_tracks_by_id(test_tracks)
        # print(len(missing_ids), len(valid_ids))
        
        
        

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Performs a backup of our local spotify library. This includes all of our followed artists and all of
                 our playlists including all track and artist data from anything in those playlists.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""    
    def backup_data(self) -> None:
        self.logger.info(f"CREATING NEW BACKUP =====================================================================")
        print(get_table_fields('tracks'))
        print(get_table_fields('playlists'))
        # self._clear_vault_playlists()
        # self._add_followed_artists_to_db()
        # self._add_user_playlists_to_db()
        # https://open.spotify.com/playlist/7Mgr45oWF0fzRzdlz0NNgT?si=a502ebb1fc8047fb
        # self.vault_db.print_playlist_tracks("7Mgr45oWF0fzRzdlz0NNgT")
        # self.verify_tracks_from_listening_data()
        
        # https://open.spotify.com/track/4mdVkJdWmb50glN1NFbUOb?si=f61baefa15a04368
        # https://open.spotify.com/track/7vaojIyvb52pVcNAWf2sG5?si=d6e3128a17294665


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════