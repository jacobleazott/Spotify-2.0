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
#  PLAYLIST GENERATORS ═══════════════════════════════════════════════════════════════════════════════════════════════
#   Generate Artist Playlist                    - reference generate_artist_playlist_from_id() / ..._from_playlist()
#   Generate Monthly Release Playlist           - reference generate_monthly_release()
#   Generate 'Generic' Artist Release Playlist  - reference generate_release_playlist()
# 
#  DATA BACKUP ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#   Spotify Library Backup                      - reference Backup_Spotify_Data.py
#   Log Playback To Databases                   - reference Log_Playback.py
# 
#  PLAYBACK MODIFIERS ════════════════════════════════════════════════════════════════════════════════════════════════
#   Shuffle Playlist                            - reference Shuffle_Styles.py
#   Skip Track                                  - reference skip_track()
# 
#  PLAYLIST ALTERATIONS ══════════════════════════════════════════════════════════════════════════════════════════════
#   Distribute Tracks To 'Collections'          - reference Misc_Features.py distribute_tracks_to_collections...()
#   Organize Playlist By Release Date           - reference Misc_Features.py reorganize_playlist()
#   Update 'Latest' Collections Playlist        - reference Misc_Features.py update_daily_latest_playlist()
# 
#  MISC FEATURES ═════════════════════════════════════════════════════════════════════════════════════════════════════
#   Get Current Playback State                  - reference get_playback_state()
#   Sanity Checks                               - reference Sanity_Tests.py
#   Weekly Listening Report                     - reference Weekly_Report.py
#   Upload Latest Backup To Google Drive        - reference upload_latest_backup_to_drive()
#   Generate List Of Most Unfollowed Artist     - reference Misc_Features.py generate_featured_artists_list()
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os

from datetime import datetime, timedelta
from glob import glob

import src.General_Spotify_Helpers as gsh
from src.helpers.decorators       import *
from src.helpers.Settings         import Settings
from src.helpers.Database_Helpers import DatabaseHelpers, get_table_fields

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
        self.logger = get_file_logger(f'logs/{log_file_name}', log_level=log_level, mode=log_mode)
        self.spotify = gsh.GeneralSpotifyHelpers(logger=self.logger)
        self.mfeatures = MiscFeatures(self.spotify, logger=self.logger)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a playlist for an artist's entire discography.
    INPUT: artist_id - Id of the artist to create for their entire discography.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_artist_playlist_from_id(self, artist_id: str) -> None:
        artist_name = self.spotify.get_artist_data(artist_id, ['name'])[0]
        self.mfeatures.generate_artist_release([artist_id], 
                                               f"{artist_name} GO THROUGH", 
                                               f"Every Track by {artist_name}")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a playlist for an artist's entire discography using a playlist to grab said artist.
    INPUT: playlist_id - Id of the playlist to grab the first artist we see (non macro)
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_artist_playlist_from_playlist(self, playlist_id: str) -> None:
        artist_id = self.mfeatures.get_first_artist_from_playlist(playlist_id)
        if artist_id is not None:
            self.generate_artist_playlist_from_id(artist_id)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a new playlist with all released tracks from the last month from all of the user's artists.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    @gsh.scopes(["user-follow-read"])
    def generate_monthly_release(self) -> None:
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        self.mfeatures.generate_artist_release(
            [artist['id'] for artist in sorted(self.spotify.get_user_artists(info=['id', 'name'])
                                                        , key=lambda ar: ar['name'].upper())]
            , f"Release Radar: {last_month.strftime("%m-%Y")}"
            , f"Releases From All Followed Artists From The Month {last_month.strftime("%m-%Y")}"
            , start_date=datetime(last_month.year, last_month.month, 1)
            , end_date=datetime(last_month.year, last_month.month, 1).replace(day=last_month.day))
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a new playlist with all released tracks within given date range for all given artists.
    INPUT: artist_ids - artist_ids we will be grabbing tracks from.
           start_date - start day of range for track collection.
           end_date - end day of range for track collection.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_release_playlist(self, artist_ids: list[str], start_date: datetime, end_date: datetime) -> None:
        self.mfeatures.generate_artist_release(
            artist_ids
            , f"Release Radar: {start_date.strftime(f"%m-%d-%Y")} -> {end_date.strftime(f"%m-%d-%Y")}"
            , f"Releases From *given* Artists From {start_date.strftime(f"%m-%d-%Y")} -> \
                                                 {end_date.strftime(f"%m-%d-%Y")}"
            , start_date=start_date
            , end_date=end_date)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Takes the user's entire spotify library (playlists, tracks, artists) and saves it off to a db.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def backup_spotify_library(self) -> None:
        BackupSpotifyData(self.spotify, logger=self.logger).backup_data()

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Log the given track_id as a listened track to our listening and track_count db's.
    INPUT: track_id - Id of track we will be logging as a 'listened' to track.
           track_name - Name of track we will be logging.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def log_playback_to_db(self, playback: dict) -> None:
        inc_tcdb = True
        # Here we decide to not increment the track_count db if we are playing a '__' playlist.
        if playback['context'] is not None and playback['context']['type'] == "playlist":
            dbh = DatabaseHelpers(logger=self.logger)
            playlist_name = next((playlist['name'] for playlist in dbh.db_get_user_playlists() 
                                  if playlist['id'] == playback['context']['id']), None)
            inc_tcdb = not any([artist for artist in dbh.db_get_user_followed_artists() 
                                if playlist_name is not None and artist['name'] == playlist_name[2:]])
        LogPlayback(logger=self.logger).log_track(playback, inc_tcdb)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates our shuffle feature and passes in our logger, spotify, and shuffle type.
    INPUT: playlist_id - Id of playlist we will be shuffling.
           shuffle_type - ShuffleType Enum of how we will shuffle the playlist (ref Shuffle_Styles.py).
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def shuffle_playlist(self, playlist_id: str, shuffle_type: ShuffleType) -> None:
        Shuffler(self.spotify, logger=self.logger).shuffle(playlist_id, shuffle_type)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Distributes given playlist tracks to their respective collections (Good, Year, __Artist).
    INPUT: playlist_id - Id of playlist we will pull tracks from to distribute.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def distribute_tracks_to_collections(self, playlist_id: str) -> None:
        self.mfeatures.distribute_tracks_to_collections_from_playlist(playlist_id)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Organizes tracks in a playlist by release date and track #. Adds the tracks back to the playlist.
                 NO DELETION OCCURS
    INPUT: playlist_id - Id of playlist we will 'organize'.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def organize_playlist_by_date(self, playlist_id: str) -> None:
        self.mfeatures.reorganize_playlist(playlist_id)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Returns the user's current playback (limited info).
    INPUT: N/A
    OUTPUT: (track_id, shuffle_state, playlist_id) of current playback.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    @gsh.scopes(["user-read-playback-state"])
    def get_playback_state(self, track_info: list[str]=get_table_fields('tracks')
                           , album_info: list[str]=get_table_fields('albums')
                           , artist_info: list[str]=get_table_fields('artists')) -> dict:
        return self.spotify.get_playback_state(track_info=track_info, album_info=album_info, artist_info=artist_info)
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Updates our "latest" playlist with the "latest" tracks in our main playlist. 
                 NOTE THIS DELETES THE "latest" PLAYLIST CONTENTS.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def update_daily_latest_playlist(self) -> None:
        self.mfeatures.update_daily_latest_playlist()
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Skips current user track.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    @gsh.scopes(["user-modify-playback-state"])
    def skip_track(self) -> None:
        self.spotify.change_playback(skip="next")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Sets the 'repeat' state of the user's playback.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    @gsh.scopes(["user-modify-playback-state"])
    def set_repeat_state(self, state: str) -> None:
        self.spotify.change_playback(repeat=state)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a weekly report of various metrics and checks on the user's collection.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_weekly_report(self) -> None:
        sanity_tester = SanityTest(logger=self.logger)
        WeeklyReport(sanity_tester, logger=self.logger).gen_weekly_report()
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Runs various santiy checks against the user's collection to verify nothing has been mismanaged.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def run_sanity_checks(self) -> None:
        sanity_tester = SanityTest(logger=self.logger)
        self.logger.info("SANITY TESTS ==========================================================")
        self.logger.info(f"Diffs In Major Playlist Sets {sanity_tester.sanity_diffs_in_major_playlist_sets()}")
        self.logger.info(f"In Progress Artists {sanity_tester.sanity_in_progress_artists()}")
        self.logger.info(f"Duplicates {sanity_tester.sanity_duplicates()}")
        self.logger.info(f"Artist Integrity {sanity_tester.sanity_artist_playlist_integrity()}")
        self.logger.info(f"Contributing Artist Check {sanity_tester.sanity_contributing_artists()}")
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Uploads the latest backup of our Spotify library to Google Drive.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def upload_latest_backup_to_drive(self) -> None:
        latest_backup = max(glob(f"{Settings.BACKUPS_LOCATION}*"), key=os.path.getmtime)
        DriveUploader(logger=self.logger).upload_file(latest_backup)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════