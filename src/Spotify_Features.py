# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    SPOTIFY FEATURES                        CREATED: 2024-09-21          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
#
#
#
# Current Features -
# 
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging as log
from datetime import datetime, timedelta
from typing import Union

import General_Spotify_Helpers as gsh
from decorators import *

# FEATURES
from Backup_Spotify_Data import BackupSpotifyData
from Log_Playback import LogPlayback

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotifyFeatures(LogAllMethods):

    def __init__(self, log_file_name: str="default", log_mode: str='a', log_level=logging.INFO) -> None:
        self.spotify = gsh.GeneralSpotifyHelpers()
        self.logger = get_file_logger(f'logs/{log_file_name}.log', log_level=log_level, mode=log_mode)
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a playlist for an artist's entire discography
    INPUT: artist_id - id of the artist to create for their entire discography
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_artist_playlist(self, artist_id: str) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        
        artist_name = self.spotify.get_artist_data(artist_id, ['name'])[0]
        self.generate_artist_release(artist_id, 
                                     f"{artist_name} GO THROUGH", 
                                     f"Every Track by {artist_name}")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a new playlist with all released tracks from the last month from all of the user's artists
    INPUT: NA
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_monthly_release(self) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"
                               , "user-follow-read"]
        
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        self.generate_artist_release(
            [artist['id'] for artist in sorted(self.spotify.get_user_artists(info=['id', 'name']), 
                                               key=lambda ar: ar['name'])],
            f"Release Radar: {last_month.strftime("%m-%Y")}",
            f"Releases From All Followed Artists From The Month {last_month.strftime("%m-%Y")}",
            start_date=datetime(last_month.year, last_month.month, 1),
            end_date=datetime(last_month.year, last_month.month, 1).replace(day=last_month.day))
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a new playlist with all released tracks within given date range for all given artists
    INPUT: artist_ids - artist_ids we will be grabbing tracks from
           start_date - start day of range for track collection
           end_date - end day of range for track collection
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_release_playlist(self, artist_ids: list[str], start_date: datetime, end_date: datetime) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        
        self.generate_artist_release(
            artist_ids, 
            f"Release Radar: {start_date.strftime(f"%m-%d-%Y")} -> {end_date.strftime(f"%m-%d-%Y")}",
            f"Releases From *given* Artists From {start_date.strftime(f"%m-%d-%Y")} -> \
                                                 {end_date.strftime(f"%m-%d-%Y")}",
            start_date=start_date,
            end_date=end_date)
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Takes the user's entire spotify library (playlists, tracks, artists) and saves it off to a db
    INPUT: NA
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def backup_spotify_library(self) -> None:
        BackupSpotifyData(self.spotify, logger=self.logger).backup_data()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Log the given track_id as a listened track to our listening and track_count db's
    INPUT: NA
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def log_playback_to_db(self, track_id: str) -> None:
        LogPlayback(logger=self.logger).log_track(track_id)
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def shuffle_playlist(self, playlist_id: str="", weighted: bool=False) -> None:
        print("not implemented")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def distribute_tracks_to_artist_playlists(self, playlist_id: str="") -> None:
        print("not implemented")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def organize_playlist_by_date(self) -> None:
        print("not implemented")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def get_playback_state(self):
        print("not done")
        
        
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPER FEATURES ════════════════════════════════════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
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
    def _generate_artist_release(self, artist_id_list: list[str], playlist_name: str, playlist_description: str,
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


def main():
    # SpotifyFeatures().generate_artist_playlist("7AB7bdCR5saJ0b9C4RuceX")
    SpotifyFeatures().backup_spotify_library()
    # SpotifyFeatures().generate_monthly_release()

if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════