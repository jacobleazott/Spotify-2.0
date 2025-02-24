# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SPOTIFY FEATURES            CREATED: 2024-02-16          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Spotify_Features.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

import unittest
from unittest import mock
from datetime import datetime, timedelta

import tests.helpers.tester_helpers as thelp

from tests.helpers.mocked_spotipy   import MockedSpotipyProxy
from src.Spotify_Features           import SpotifyFeatures
from src.features.Shuffle_Styles    import ShuffleType
from src.helpers.Settings           import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Spotify Features functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestSpotifyFeatures(unittest.TestCase):
    
    @mock.patch('src.General_Spotify_Helpers.SpotipyProxy', new=MockedSpotipyProxy)
    @mock.patch('src.Spotify_Features.MiscFeatures')
    def setUp(self, MockMiscFeatures):
        self.spotify_features = SpotifyFeatures()
        self.mock_misc_features = MockMiscFeatures()
        self.addCleanup(self.verify_scopes)
    
    def verify_scopes(self):
        assert self.spotify_features.spotify._scopes == []
    
    @mock.patch('src.Spotify_Features.MiscFeatures')
    @mock.patch('src.General_Spotify_Helpers.GeneralSpotifyHelpers')
    @mock.patch('src.Spotify_Features.get_file_logger')
    def test_init(self, MockGetFileLogger, MockGSH, MockMiscFeatures):
        self.setUp = lambda: None # Don't Run setUp()
        features = SpotifyFeatures(log_file_name='test.log', log_mode='w', log_level=10)

        MockGetFileLogger.assert_called_once_with('logs/test.log', mode='w', log_level=10)
        MockGSH.assert_called_once_with(logger=MockGetFileLogger())
        MockMiscFeatures.assert_called_once_with(MockGSH(), logger=MockGetFileLogger())
        self.assertEqual(features.logger, MockGetFileLogger())
        self.assertEqual(features.spotify, MockGSH())
        self.assertEqual(features.mfeatures, MockMiscFeatures())
    
    def test_generate_artist_playlist_from_id(self):
        thelp.create_env(self.spotify_features.spotify)
        self.spotify_features.generate_artist_playlist_from_id('Ar005')
        self.mock_misc_features.generate_artist_release.assert_called_once_with(['Ar005']
                                                                                , 'Fake Artist 5 GO THROUGH'
                                                                                , mock.ANY)
    
    def test_generate_artist_playlist_from_playlist(self):
        thelp.create_env(self.spotify_features.spotify)
        self.mock_misc_features.get_first_artist_from_playlist.return_value = 'Ar002'
        self.spotify_features.generate_artist_playlist_from_playlist('Pl002')
        self.mock_misc_features.get_first_artist_from_playlist.assert_called_once_with('Pl002')
        self.mock_misc_features.generate_artist_release.assert_called_once_with(['Ar002']
                                                                                , 'Fake Artist 2 GO THROUGH'
                                                                                , mock.ANY)
    
    def test_generate_monthly_release(self):
        thelp.create_env(self.spotify_features.spotify)
        self.spotify_features.generate_monthly_release()
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        expected_start_date = datetime(last_month.year, last_month.month, 1)
        expected_end_date = datetime(last_month.year, last_month.month, last_month.day)
        self.mock_misc_features.generate_artist_release.assert_called_once_with(
                                            ['Ar002', 'Ar003', 'Ar004']
                                            , mock.ANY, mock.ANY
                                            , start_date=expected_start_date, end_date=expected_end_date)
    
    def test_generate_release_playlist(self):
        thelp.create_env(self.spotify_features.spotify)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2029, 12, 31)
        artist_ids = ['Ar001', 'Ar002', 'Ar111']
        self.spotify_features.generate_release_playlist(artist_ids, start_date, end_date)
        self.mock_misc_features.generate_artist_release.assert_called_once_with(artist_ids, mock.ANY, mock.ANY
                                                                    , start_date=start_date, end_date=end_date)

    @mock.patch('src.Spotify_Features.BackupSpotifyData')
    def test_backup_spotify_library(self, MockBackupSpotifyData):
        self.spotify_features.backup_spotify_library()
        MockBackupSpotifyData.assert_called_once_with(self.spotify_features.spotify
                                                      , logger=self.spotify_features.logger)
        MockBackupSpotifyData().backup_data.assert_called_once()

    @mock.patch('src.Spotify_Features.LogPlayback')
    @mock.patch('src.Spotify_Features.DatabaseHelpers')
    def test_log_playback_to_db(self, MockDatabaseHelpers, MockLogPlayback):
        mock_db_helpers = MockDatabaseHelpers.return_value
        mock_db_helpers.db_get_user_followed_artists.return_value = [{'name': 'Artist 1'}]
        playback = {'context': {'type': 'playlist', 'id': 'Pl002'}}
        
        # Test __ playlist That its not incremented
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.assert_called_once_with(logger=self.spotify_features.logger)
        MockLogPlayback().log_track.assert_called_once_with(playback, False)
        MockLogPlayback().log_track.reset_mock()
        
        # Test __ playlist that I don't follow to increment
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 2'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, True)
        MockLogPlayback().log_track.reset_mock()
        
        # Test Incorrect __ playlist
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '_Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, True)
        MockLogPlayback().log_track.reset_mock()
        
        # Test unknown playlist
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl001', 'name': '_Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, True)
        MockLogPlayback().log_track.reset_mock()
        
        # Test multiple artists, multiple playlists
        mock_db_helpers.db_get_user_followed_artists. return_value = [{'name': 'Artist 1'}
                                                                     , {'name': 'Artist 22'}
                                                                     , {'name': 'Artist 3'}]     
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 1'}
                                                              , {'id': 'Pl003', 'name': 'EMPTY'}
                                                              , {'id': 'Pl004', 'name': '__Artist 3'}]
        playback = {'context': {'type': 'playlist', 'id': 'Pl004'}}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, False)
        MockLogPlayback().log_track.reset_mock()
        
        # Test None context
        playback = {'context': None}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, True)
        MockLogPlayback().log_track.reset_mock()
        
        # Test non playlist context
        playback = {'context': {'type': 'album', 'id': 'Al002'}}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback().log_track.assert_called_once_with(playback, True)
        MockLogPlayback().log_track.reset_mock()
    
    @mock.patch('src.Spotify_Features.Shuffler')
    def test_shuffle_playlist(self, MockShuffler):
        playlist_id = 'test_playlist_id'
        for shuffle in ShuffleType:
            self.spotify_features.shuffle_playlist(playlist_id, shuffle)
            MockShuffler.assert_called_once_with(self.spotify_features.spotify, logger=self.spotify_features.logger)
            MockShuffler().shuffle.assert_called_once_with(playlist_id, shuffle)
            MockShuffler.reset_mock()
    
    def test_distribute_tracks_to_collections(self):
        playlist_id = 'test_playlist_id'
        self.spotify_features.distribute_tracks_to_collections(playlist_id)
        self.mock_misc_features.distribute_tracks_to_collections_from_playlist.assert_called_once_with(playlist_id)

    def test_organize_playlist_by_date(self):
        playlist_id = 'test_playlist_id'
        self.spotify_features.organize_playlist_by_date(playlist_id)
        self.mock_misc_features.reorganize_playlist.assert_called_once_with(playlist_id)
    
    @mock.patch('src.General_Spotify_Helpers.GeneralSpotifyHelpers.get_playback_state')
    def test_get_playback_state(self, MockGetPlaybackState):
        self.spotify_features.get_playback_state()
        MockGetPlaybackState.assert_called_once_with(track_info=['id', 'name'])
        MockGetPlaybackState.reset_mock()
        
        self.spotify_features.get_playback_state(track_info=['test1','test2'])
        MockGetPlaybackState.assert_called_once_with(track_info=['test1', 'test2'])
        MockGetPlaybackState.reset_mock()
    
    def test_update_daily_latest_playlist(self):
        self.spotify_features.update_daily_latest_playlist()
        self.mock_misc_features.update_daily_latest_playlist.assert_called_once()
    
    @mock.patch('src.General_Spotify_Helpers.GeneralSpotifyHelpers.change_playback')
    def test_skip_track(self, MockChangePlayback):
        self.spotify_features.skip_track()
        MockChangePlayback.assert_called_once_with(skip="next")
    
    @mock.patch('src.Spotify_Features.WeeklyReport')
    @mock.patch('src.Spotify_Features.SanityTest')
    def test_generate_weekly_report(self, MockSanityTest, MockWeeklyReport):
        mock_sanity_instance = mock.MagicMock()
        MockSanityTest.return_value = mock_sanity_instance
        self.spotify_features.generate_weekly_report()

        MockSanityTest.assert_called_once_with(logger=self.spotify_features.logger)
        MockWeeklyReport.assert_called_once_with(mock_sanity_instance, logger=self.spotify_features.logger)
        MockWeeklyReport().gen_weekly_report.assert_called_once()
    
    @mock.patch('src.Spotify_Features.SanityTest')
    def test_run_sanity_checks(self, MockSanityTest):
        self.spotify_features.run_sanity_checks()
        MockSanityTest.assert_called_once_with(logger=self.spotify_features.logger)
        expected_calls = [mock.call.sanity_diffs_in_major_playlist_sets()
                          , mock.call.sanity_in_progress_artists()
                          , mock.call.sanity_duplicates()
                          , mock.call.sanity_artist_playlist_integrity() 
                          , mock.call.sanity_contributing_artists()]

        actual_calls = [call for call in MockSanityTest().mock_calls if '__str__' not in str(call)]
        self.assertCountEqual(actual_calls, expected_calls)
    
    @mock.patch('src.Spotify_Features.DriveUploader')
    @mock.patch('src.Spotify_Features.glob')
    @mock.patch('os.path.getmtime')
    def test_latest_backup(self, mock_getmtime, mock_glob, MockDriveUploader):
        # Define your mocked file paths
        mock_glob.return_value = ['/path/to/file1.txt'
                                  , '/path/to/file2.txt'
                                  , '/path/to/file3.txt']
        # Mock the modification times
        mock_getmtime.side_effect = lambda path: {'/path/to/file1.txt': 100
                                                  , '/path/to/file2.txt': 200
                                                  , '/path/to/file3.txt': 300}[path]
        
        self.spotify_features.upload_latest_backup_to_drive()
        MockDriveUploader.assert_called_once_with(logger=self.spotify_features.logger)
        MockDriveUploader().upload_file.assert_called_once_with('/path/to/file3.txt')

        # Verify that glob and getmtime were called correctly
        mock_glob.assert_called_once_with(f"{Settings.BACKUPS_LOCATION}*")
        mock_getmtime.assert_any_call('/path/to/file1.txt')
        mock_getmtime.assert_any_call('/path/to/file2.txt')
        mock_getmtime.assert_any_call('/path/to/file3.txt')
    
    def test_print_most_featured_artists(self):
        self.mock_misc_features.generate_featured_artists_list.return_value = [
            ('Artist Id 1', ['Artist 1', 5, ['Artist 10'], ['Track 1']])
          , ('Artist Id 2', ['Artist 2', 8, ['Artist 20'], ['Track 2']])]
        self.spotify_features.print_most_featured_artists()
        self.mock_misc_features.generate_featured_artists_list.assert_called_once()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════