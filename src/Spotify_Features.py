# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIFY FEATURES                         CREATED: 2024-09-21          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
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
#   PLAYLIST GENERATORS ═══════════════════════════════════════════════════════════════════════════════════════════════
#   Generate Artist Playlist                    - reference generate_artist_playlist_from_id() / ..._from_playlist()
#   Generate Monthly Release Playlist           - reference generate_monthly_release()
#   Generate 'Generic' Artist Release Playlist  - reference generate_release_playlist()
#
#   DATA BACKUP ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#   Spotify Library Backup                      - reference Backup_Spotify_Data.py
#   Log Playback To Databases                   - reference Log_Playback.py
#
#   PLAYBACK MODIFIERS ════════════════════════════════════════════════════════════════════════════════════════════════
#   Shuffle Playlist                            - reference Shuffle_Styles.py
#   Skip Track                                  - reference skip_track()
#
#   PLAYLIST ALTERATIONS ══════════════════════════════════════════════════════════════════════════════════════════════
#   Distribute Tracks To 'Collections'          - reference Misc_Features.py distribute_tracks_to_collections...()
#   Organize Playlist By Release Date           - reference Misc_Features.py reorganize_playlist()
#
#   MISC FEATURES ═════════════════════════════════════════════════════════════════════════════════════════════════════
#   Get Current Playback State                  - reference get_playback_state()
#   Sanity Checks                               - reference Sanity_Tests.py
#   Weekly Listening Report                     - reference Weekly_Report.py
#   Upload Latest Backup To Google Drive        - reference upload_latest_backup_to_drive()
#
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import time

from datetime import datetime, timedelta
from glob import glob
from typing import Union

import src.General_Spotify_Helpers as gsh
from src.helpers.decorators import *
from src.helpers.Settings import Settings

# FEATURES
from src.features.Misc_Features         import MiscFeatures
from src.features.Backup_Spotify_Data   import BackupSpotifyData
from src.features.Google_Drive_Uploader import DriveUploader
from src.features.Log_Playback          import LogPlayback
from src.features.Sanity_Tests          import SanityTest
from src.features.Shuffle_Styles        import Shuffler, ShuffleType
from src.features.Weekly_Report         import WeeklyReport

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Collection of all of our Spotify API features. Handles and abstracts our GSH object.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotifyFeatures(LogAllMethods):

    def __init__(self, log_file_name: str="default.log", log_mode: str='a', log_level=logging.INFO) -> None:
        self.spotify = gsh.GeneralSpotifyHelpers()
        self.logger = get_file_logger(f'logs/{log_file_name}', log_level=log_level, mode=log_mode)
        self.mfeatures = MiscFeatures(self.spotify, logger=self.logger)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a playlist for an artist's entire discography.
    INPUT: artist_id - Id of the artist to create for their entire discography.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_artist_playlist_from_id(self, artist_id: str) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        
        artist_name = self.spotify.get_artist_data(artist_id, ['name'])[0]
        self.mfeatures.generate_artist_release([artist_id], 
                                               f"{artist_name} GO THROUGH", 
                                               f"Every Track by {artist_name}")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a playlist for an artist's entire discography using a playlist to grab said artist.
    INPUT: playlist_id - Id of the playlist to grab the first artist we see (non macro)
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_artist_playlist_from_playlist(self, playlist_id: str) -> None:
        self.spotify.scopes = ["playlist-read-private"]
        
        artist_id = self.mfeatures.get_first_artist_from_playlist(playlist_id)
        self.generate_artist_playlist_from_id(artist_id)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a new playlist with all released tracks from the last month from all of the user's artists.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
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
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a new playlist with all released tracks within given date range for all given artists.
    INPUT: artist_ids - artist_ids we will be grabbing tracks from.
           start_date - start day of range for track collection.
           end_date - end day of range for track collection.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
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
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Takes the user's entire spotify library (playlists, tracks, artists) and saves it off to a db.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def backup_spotify_library(self) -> None:
        BackupSpotifyData(self.spotify, logger=self.logger).backup_data()

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Log the given track_id as a listened track to our listening and track_count db's.
    INPUT: track_id - Id of track we will be logging as a 'listened' to track.
           track_name - Name of track we will be logging.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def log_playback_to_db(self, track_id: str, track_name: str, playlist_id: str) -> None:
        # Determine if we should 
        LogPlayback(logger=self.logger).log_track(track_id, track_name)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates our shuffle feature and passes in our logger, spotify, and shuffle type.
    INPUT: playlist_id - Id of playlist we will be shuffling.
           shuffle_type - ShuffleType Enum of how we will shuffle the playlist (ref Shuffle_Styles.py).
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def shuffle_playlist(self, playlist_id: str, shuffle_type: ShuffleType) -> None:
        Shuffler(self.spotify, logger=self.logger).shuffle(playlist_id, shuffle_type)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Distributes given playlist tracks to their respective collections (Good, Year, __Artist).
    INPUT: playlist_id - Id of playlist we will pull tracks from to distribute.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def distribute_tracks_to_collections(self, playlist_id: str) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"
                               , "user-follow-read"]
        self.mfeatures.distribute_tracks_to_collections_from_playlist(playlist_id)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Organizes tracks in a playlist by release date and track #. Adds the tracks back to the playlist.
                 NO DELETION OCCURS
    INPUT: playlist_id - Id of playlist we will 'organize'.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def organize_playlist_by_date(self, playlist_id: str) -> None:
        self.spotify.scopes = [  "playlist-modify-public"
                               , "playlist-modify-private"
                               , "playlist-read-private"]
        self.mfeatures.reorganize_playlist(playlist_id)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Returns the user's current playback (limited info).
    INPUT: NA
    OUTPUT: (track_id, shuffle_state, playlist_id) of current playback.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_playback_state(self) -> tuple[str, str, bool, str]:
        return self.spotify.get_playback_state()
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Updates our "latest" playlist with the "latest" tracks in our main playlist. 
                 NOTE THIS DELETES THE "latest" PLAYLIST CONTENTS.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def update_daily_latest_playlist(self) -> None:
        self.spotify.scopes = [  "playlist-read-private"
                               , "playlist-read-collaborative"
                               , "playlist-modify-public"
                               , "playlist-modify-private"
                               , Settings.DELETE_SCOPE]
        self.mfeatures.update_daily_latest_playlist()
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Skips current user track.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def skip_track(self) -> None:
        self.spotify.change_playback(skip="next")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a weekly report of various metrics and checks on the user's collection.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_weekly_report(self) -> None:
        sanity_tester = SanityTest(logger=self.logger)
        WeeklyReport(sanity_tester, logger=self.logger).gen_weekly_report()
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Runs various santiy checks against the user's collection to verify nothing has been mismanaged.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def run_sanity_checks(self) -> None:
        sanity_tester = SanityTest(logger=self.logger)
        logger.info("SANITY TESTS ==========================================================")
        logger.info(f"Diffs In Major Playlist Sets {sanity_tester.sanity_diffs_in_major_playlist_sets()}")
        logger.info(f"In Progress Artists {sanity_tester.sanity_in_progress_artists()}")
        logger.info(f"Duplicates {sanity_tester.sanity_duplicates()}")
        logger.info(f"Artist Integrity {sanity_tester.sanity_artist_playlist_integrity()}")
        logger.info(f"Contributing Artist Check {sanity_tester.sanity_contributing_artists()}")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Uploads the latest backup of our Spotify library to Google Drive.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def upload_latest_backup_to_drive(self) -> None:
        latest_backup = max(glob(f"{Settings.BACKUPS_LOCATION}*"), key=os.path.getmtime)
        DriveUploader(logger=self.logger).upload_file(latest_backup)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════