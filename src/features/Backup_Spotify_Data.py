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
from datetime import datetime

import src.General_Spotify_Helpers as gsh

from src.helpers.Database_Helpers   import DatabaseHelpers, DatabaseSchema, get_table_fields, build_entries_from_tracks
from src.helpers.decorators         import *
from src.helpers.Settings           import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class BackupSpotifyData(LogAllMethods):
    
    def __init__(self, spotify, backup_db_path: str=None, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        self.vault_db = DatabaseHelpers(Settings.LISTENING_VAULT_DB, logger=self.logger)
        
        snapshot_db_path = backup_db_path or f"{Settings.BACKUPS_LOCATION}playlist_snapshot_{datetime.today().date()}.db"
        self.snapshot_db = DatabaseHelpers(snapshot_db_path, schema=DatabaseSchema.SNAPSHOT
                                           , logger=self.logger)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Clears the vault database of it's playlist and user data.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _clear_vault_playlists(self) -> None:
        self.logger.info(f"\t Clearing Vault Playlists")
        
        with self.vault_db.connect_db() as db_conn:
            db_conn.execute("DELETE FROM playlists_tracks;")
            db_conn.execute("DELETE FROM playlists;")
            db_conn.execute("DELETE FROM followed_artists;")
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Adds a list of entries to both of our databases.
    INPUT: table - SQLite table to insert into.
           values - List of entries to insert.
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
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
        tracks = self.spotify.get_playlist_tracks(playlist_id
                                                , track_info=get_table_fields('tracks')
                                                , album_info=get_table_fields('albums') + ['artists']
                                                , artist_info=get_table_fields('artists'))
        
        self.logger.debug(f"\tTracks #: {len(tracks)}")
        
        entries = build_entries_from_tracks(tracks, playlist_id=playlist_id)
        for table, values in entries.items():
            self._insert_into_databases(table, values)
    
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

        self.logger.info(f"\t Inserted {self.snapshot_db.get_table_size('tracks')} Tracks")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Performs a backup of our local spotify library. This includes all of our followed artists and all of
                 our playlists including all track and artist data from anything in those playlists.
    INPUT: N/A
    Output: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""    
    def backup_data(self) -> None:
        self.logger.info(f"CREATING NEW BACKUP =====================================================================")
        self._clear_vault_playlists()
        self._add_followed_artists_to_db()
        self._add_user_playlists_to_db()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════