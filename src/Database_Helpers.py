import logging
import os
import sqlite3

from glob import glob

from decorators import *

class DatabaseHelpers(LogAllMethods):
    
    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        
        latest_backup_file = max(glob('databases/backups/*'), key=os.path.getmtime)
        self.backup_db_conn = sqlite3.connect(latest_backup_file)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: This grabs the tracks from a playlist if we have it in our database. If we don't have it locally we
                 will go and grab it from spotify directly but this takes much much longer than doing it locally.
    INPUT: playlist_id - Id of playlist we will be grabbing tracks from.
           grab_from_spotify - If we should grab directly from spotify regardless if we have them locally.
    OUTPUT: List of track id's.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def db_get_tracks_from_playlist(self, playlist_id: str, grab_from_spotify: bool=False) -> list[str]:
        query = f"""
                SELECT tracks.*
                FROM tracks
                JOIN playlists_tracks ON tracks.id = playlists_tracks.id_track
                WHERE playlists_tracks.id_playlist = '{playlist_id}'
                """
        playlist_tracks = [track[0] for track in self.backup_db_conn.execute(query).fetchall()]
        self.backup_db_conn.close()
            
        if len(playlist_tracks) == 0 or grab_from_spotify:
            playlist_tracks = [track['id'] for track in self.spotify.get_playlist_tracks(playlist_id) 
                  if track['id'] is not None]
            
        return [track for track in playlist_tracks if track not in MACRO_LIST]

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def db_get_track_artists(self, track_id):
        return [artist[0] for artist in self.backup_db_conn.execute(f"""SELECT artists.name 
                                FROM 'artists'
                                JOIN 'tracks_artists' ON artists.id = tracks_artists.id_artist
                                WHERE tracks_artists.id_track = '{track_id}'""").fetchall()]