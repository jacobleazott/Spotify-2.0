# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    SPOTIFY FEATURES                        CREATED: 2024-09-21          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file contains the overarching "Spotify Feature" library. As all roads lead to roam, all features lead here.
#   The idea is any given capability or feature should solely be accessed through here. This class will handle the
#   GSH object, scopes, logging, and other feature level management. The end user in the applications should only
#   ever have to instantiate this and choose which features they wish to use. No additional involvement needed.
#
# The paradigm of feature implementations is that if it is complicated enough to need multiple functions/ helpers it
#   goes into it's own file/ class where 'SpotifyFeatures' will pass all appropriate args, our GSH object, and logger.
#   The individual feature should define it's own scope needs (currently 'FEATURE_SCOPES') and apply them themselves.
#
# CURRENT FEATURES -
#
#   PLAYLIST GENERATORS ══════════════════════════════════════════════════════════════════════════════════════════════
#   Generate Artist Playlist                    - reference generate_artist_playlist()
#   Generate Monthly Release Playlist           - reference generate_monthly_release()
#   Generate 'Generic' Artist Release Playlist  - reference generate_release_playlist()
#
#   DATA BACKUP ══════════════════════════════════════════════════════════════════════════════════════════════════════
#   Spotify Library Backup                      - reference Backup_Spotify_Data.py
#   Log Playback To Databases                   - reference Log_Playback.py
#
#   PLAYBACK MODIFIERS ═══════════════════════════════════════════════════════════════════════════════════════════════
#   Shuffle Playlist                            - reference Shuffle_Styles.py
#
#   PLAYLIST ALTERATIONS ═════════════════════════════════════════════════════════════════════════════════════════════
#   Distribute Tracks To 'Collections'          - reference
#   Organize Playlist By Release Date           - reference
#
#   MISC FEATURES ════════════════════════════════════════════════════════════════════════════════════════════════════
#   Get Current Playback State                  - reference get_playback_state()
#   Sanity Checks                               - reference Sanity_Tests.py
#   Weekly Listening Report                     - reference Weekly_Report.py
#
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging as log
from datetime import datetime, timedelta
from typing import Union

import General_Spotify_Helpers as gsh
from decorators import *

# FEATURES
from Misc_Features import MiscFeatures
from Backup_Spotify_Data import BackupSpotifyData
from Log_Playback import LogPlayback
from Shuffle_Styles import Shuffler, ShuffleType

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotifyFeatures(LogAllMethods):

    def __init__(self, log_file_name: str="default", log_mode: str='a', log_level=logging.INFO) -> None:
        self.spotify = gsh.GeneralSpotifyHelpers()
        self.logger = get_file_logger(f'logs/{log_file_name}.log', log_level=log_level, mode=log_mode)
        self.mfeatures = MiscFeatures(self.spotify, logger=self.logger)
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a playlist for an artist's entire discography.
    INPUT: artist_id - id of the artist to create for their entire discography.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_artist_playlist(self, artist_id: str) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        
        artist_name = self.spotify.get_artist_data(artist_id, ['name'])[0]
        self.mfeatures.generate_artist_release(artist_id, 
                                               f"{artist_name} GO THROUGH", 
                                               f"Every Track by {artist_name}")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a new playlist with all released tracks from the last month from all of the user's artists.
    INPUT: NA
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_monthly_release(self) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"
                               , "user-follow-read"]
        
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        self.mfeatures.generate_artist_release(
            [artist['id'] for artist in sorted(self.spotify.get_user_artists(info=['id', 'name']), 
                                               key=lambda ar: ar['name'])],
            f"Release Radar: {last_month.strftime("%m-%Y")}",
            f"Releases From All Followed Artists From The Month {last_month.strftime("%m-%Y")}",
            start_date=datetime(last_month.year, last_month.month, 1),
            end_date=datetime(last_month.year, last_month.month, 1).replace(day=last_month.day))
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a new playlist with all released tracks within given date range for all given artists.
    INPUT: artist_ids - artist_ids we will be grabbing tracks from.
           start_date - start day of range for track collection.
           end_date - end day of range for track collection.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_release_playlist(self, artist_ids: list[str], start_date: datetime, end_date: datetime) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        
        self.mfeatures.generate_artist_release(
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
    DESCRIPTION: Log the given track_id as a listened track to our listening and track_count db's.
    INPUT: track_id - id of track we will be logging as a 'listened' to track.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def log_playback_to_db(self, track_id: str) -> None:
        LogPlayback(logger=self.logger).log_track(track_id)
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def shuffle_playlist(self, playlist_id: str="", shuffle_type: ShuffleType=ShuffleType.RANDOM) -> None:
        print("not imported")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def distribute_tracks_to_artist_playlists(self, playlist_id: str="") -> None:
        print("not imported")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def organize_playlist_by_date(self) -> None:
        print("not imported")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def get_playback_state(self):
        print("not imported")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generate_weekly_report(self):
        print("not imported")
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def run_sanity_checks(self):
        print("not imported")
        

# TESTING TESTING TESTING
def main():
    # SpotifyFeatures().generate_artist_playlist("7AB7bdCR5saJ0b9C4RuceX")
    SpotifyFeatures().backup_spotify_library()
    # SpotifyFeatures().generate_monthly_release()

if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════