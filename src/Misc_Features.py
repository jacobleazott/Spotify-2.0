# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    MISC FEATURES                           CREATED: 2024-09-22          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file contains simple misc features. Only features that can be comfortably done in one function should be in
#   this file. If it requires anything additional it should receive its own dedicated file.
#
# Current Features:
#   generate_artist_release - Takes given artist_id(s), playlist name, playlist desc, start/ end date, and creates a 
#                               new playlist with all the tracks from those artists released within the given dates.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
from decorators import *

import General_Spotify_Helpers as gsh

class MiscFeatures(LogAllMethods):
    
    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if not None else logger.getLogger()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Generates a new playlist of released tracks within the given date range for the given artists
    INPUT: artist_id_list - list of spotify artist_id's we want to gather tracks from
           playlist_name - name that the new playlist will be given
           playlist_description - description that the new playlist will be given
           start_date - start day of track collection
           end_date - end day of track collection
           logger - logger object used
    OUTPUT: str of playlist_id created
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_artist_release(self, artist_id_list: list[str], playlist_name: str, playlist_description: str,
                start_date: Optional[datetime]=None, end_date: Optional[datetime]=None) -> str:
        playlist_id = self.spotify.create_playlist(playlist_name, description=playlist_description)
        self.logger.info(f"Created New Playlist: {playlist_id}")
        
        tracks = []
        for artist_id in artist_id_list:
            self.logger.info(f"finding tracks for {artist_id}")
            tmp_tracks = self.spotify.gather_tracks_by_artist(artist_id, 
                                                          start_date=start_date, 
                                                          end_date=end_date)
            self.logger.info(f"\tFound {len(tmp_tracks)} tracks")
            tracks += tmp_tracks
            
        self.logger.info(f"Adding {len(tracks)} tracks to playlist {playlist_id}")
        self.logger.debug(f"Tracks: {tracks}")
        self.spotify.add_tracks_to_playlist(playlist_id, tracks)
        
        return playlist_id
    
# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════



