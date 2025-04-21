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

from src.helpers.Database_Helpers   import DatabaseHelpers, DatabaseSchema
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
        
        snapshot_db_path = backup_db_path or f"{Settings.BACKUPS_LOCATION}{datetime.today().date()}.db"
        self.snapshot_db = DatabaseHelpers(db_path = snapshot_db_path, schema=DatabaseSchema.SNAPSHOT
                                           , logger=self.logger)
       
    def _clear_vault_playlists(self) -> None:
        self.logger.info(f"\t Clearing Vault Playlists")
        
        with self.vault_db.connect_db() as db_conn:
            db_conn.execute("DELETE FROM playlists_tracks;")
            db_conn.execute("DELETE FROM playlists;")
    
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
        user_playlists = self.spotify.get_user_playlists(info=["id", "name", "description"])
        self.logger.info(f"\t Inserting {len(user_playlists)} Playlists")
        self._insert_into_databases("playlists", user_playlists)
        
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
        self._add_followed_artists_to_db()
        self._add_user_playlists_to_db()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════