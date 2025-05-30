# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    STATISTICS                               CREATED: 2025-03-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Various functions that generate statistics about the Spotify data we have. 
#
#  generate_featured_artists_list - Generates a list of all contributing artists from our collection that we do not 
#                                      currently follow. Attached data is how many tracks they appear on and how many
#                                      unique artists they collaborate with in our followed artists.
#
#  generate_latest_artists - Generates a list of artists that we have listened to the most in the last specified time
#                               period. It sorts in descending order by total minutes listened.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import os
import sqlite3

from datetime import datetime
from glob import glob

from src.helpers.decorators       import *
from src.helpers.Settings         import Settings
from src.helpers.Database_Helpers import DatabaseHelpers

class SpotifyStatistics(LogAllMethods):
    
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else logging.getLogger()
        self.vault_db = DatabaseHelpers(Settings.LISTENING_VAULT_DB,logger=self.logger)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a list of all artists that appear in our 'Master' collection that we do not follow.
                 This list is ordered first by # of unique artists we follow that they appear with followed by total
                 number of tracks they appear on.
    INPUT: num_artists - Number of artists to return.
    OUTPUT: List of our featured artists that we do not follow sorted.
            {<artist_id>: (<artist_name>, <num_tracks_appeared_on>, <followed_artists>, <tracks_appeared_on>),}
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_featured_artists_list(self, num_artists: int) -> list:
        playlists_to_search = [Settings.MASTER_MIX_ID, Settings.CHRISTMAS_MASTER_MIX_ID]
        followed_artist_ids = set(artist['id'] for artist in self.vault_db.get_user_followed_artists())
        
        ignored_track_ids = set(track['id'] for playlist_id in Settings.PLAYLIST_IDS_NOT_IN_ARTISTS
                                for track in self.vault_db.get_tracks_from_playlist(playlist_id))
        
        artist_appearances = [artist for artist in self.vault_db.get_artists_and_their_collabs_from_playlists(playlists_to_search, exclude_artists=followed_artist_ids)
                              if artist['id'] not in followed_artist_ids]
        
        all_playlists_tracks = set(track['id'] for playlist_id in playlists_to_search
                                   for track in self.vault_db.get_tracks_from_playlist(playlist_id))
        
        artist_data = []
        for artist in artist_appearances:
            unique_artists = [ar['name'] for ar in artist['appears_with'] if ar['id'] in followed_artist_ids]

            tracks = [track['name'] for track in self.vault_db.get_artist_tracks(artist['id']) 
                      if track['id'] not in ignored_track_ids and track['id'] in all_playlists_tracks
                      and any(artist['id'] in followed_artist_ids for artist in self.vault_db.get_track_artists(track['id']))]
            
            if len(unique_artists) == 0 or len(tracks) == 0:
                continue
            
            artist_data.append({
                'Artist Name': artist['name']
              , 'Number of Tracks':len(tracks)
              , 'Unique Artists': [ar['name'] for ar in artist['appears_with'] if ar['id'] in followed_artist_ids]
              , 'Track Names': tracks
            })
        
        return sorted(artist_data
                    , key=lambda artist: (artist['Number of Tracks'] + 2 * len(artist['Unique Artists']))
                    , reverse=True)[:num_artists]
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a list of the artists that we have listened to the most in the last specified time period.
    INPUT: start_date - The start date of the time period we want to generate the list for.
           end_date   - The end date of the time period we want to generate the list for.
           num_artists - Number of artists to return.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_latest_artists(self, start_date, end_date=datetime.now(), num_artists=5):
        artist_counts = self.vault_db.get_artists_listened_in_date_range(start_date, end_date)
        return [{'Artist': artist['name'], 'Listening Time (min)': artist['artist_count'] / 4} 
                for artist in artist_counts[:num_artists]]


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════