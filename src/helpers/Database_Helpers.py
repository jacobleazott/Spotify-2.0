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
import logging
import os
import sqlite3
from glob import glob

from src.helpers.decorators import *
from src.helpers.Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Collection of methods similar to GSH that grab from our latest local backup rather than spotify itself.
             Table definitions can be found in Backup_Spotify_Data.py.
             The Database we use is just the latest from our Backup_Spotify_Data location.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class DatabaseHelpers(LogAllMethods):
    
    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        
        latest_backup_file = max(glob(f"{Settings.BACKUPS_LOCATION}*"), key=os.path.getmtime)
        self.backup_db_conn = sqlite3.connect(latest_backup_file)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Since we want to return dicts and not lists of our db data we can use this method to grab our db 
                 column names and zip it up into a dictionary for us.
    INPUT: query - Sqlite query we will fetchall results from and turn into a dict.
    OUTPUT: List of dicts from the db query.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _conn_query_to_dict(self, query: str) -> list[dict]:
        cursor = self.backup_db_conn.execute(query)
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
            WHERE playlists_tracks.id_playlist = '{playlist_id}'
        """
        return self._conn_query_to_dict(query)

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
            WHERE tracks_artists.id_track = '{track_id}'
        """
        return self._conn_query_to_dict(query)
   
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs all of the playlists in our db.
    INPUT: NA
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
    INPUT: NA
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