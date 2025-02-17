import unittest
from unittest import mock
from datetime import datetime, timedelta
from pprint import pprint

from src.Spotify_Features import SpotifyFeatures
from src.features.Shuffle_Styles import ShuffleType
import tests.helpers.tester_helpers as thelp
import src.General_Spotify_Helpers as gsh

from tests.helpers.mocked_spotipy import MockedSpotipyProxy

class TestSpotifyFeatures(unittest.TestCase):
    
    # @patch('src.Spotify_Features.gsh.GeneralSpotifyHelpers')
    # @patch('src.Spotify_Features.MiscFeatures')
    # def setUp(self, MockMiscFeatures, MockGeneralSpotifyHelpers):
    #     self.mock_misc_features = MockMiscFeatures.return_value
    #     self.mock_spotify_helpers = MockGeneralSpotifyHelpers.return_value
    #     self.spotify_features = SpotifyFeatures()
    
    @mock.patch('src.General_Spotify_Helpers.SpotipyProxy', new=MockedSpotipyProxy)
    def setUp(self):
        self.spotify_features = SpotifyFeatures()

    def test_generate_artist_playlist_from_id(self):
        thelp.create_env(self.spotify_features.spotify)
        with mock.patch.object(self.spotify_features.mfeatures, 'generate_artist_release') as mock_method:
            self.spotify_features.generate_artist_playlist_from_id('Ar005')
            mock_method.assert_called_with(['Ar005'], 'Fake Artist 5 GO THROUGH', mock.ANY)
            
    def test_generate_artist_playlist_from_playlist(self):
        thelp.create_env(self.spotify_features.spotify)
        with mock.patch.object(self.spotify_features.mfeatures, 'generate_artist_release') as mock_method:
            self.spotify_features.generate_artist_playlist_from_playlist('Pl002')
            mock_method.assert_called_with(['Ar002'], 'Fake Artist 2 GO THROUGH', mock.ANY)
            
    def test_generate_monthly_release(self):
        thelp.create_env(self.spotify_features.spotify)
        with mock.patch.object(self.spotify_features.mfeatures, 'generate_artist_release') as mock_method:
            self.spotify_features.generate_monthly_release()
            last_month = datetime.today().replace(day=1) - timedelta(days=1)
            expected_start_date = datetime(last_month.year, last_month.month, 1)
            expected_end_date = datetime(last_month.year, last_month.month, last_month.day)
            mock_method.assert_called_with(['Ar002', 'Ar003', 'Ar004'], mock.ANY, mock.ANY
                                           , start_date=expected_start_date, end_date=expected_end_date)
            
    def test_generate_release_playlist(self):
        thelp.create_env(self.spotify_features.spotify)
        with mock.patch.object(self.spotify_features.mfeatures, 'generate_artist_release') as mock_method:
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2029, 12, 31)
            artist_ids = ['Ar001', 'Ar002', 'Ar111']
            self.spotify_features.generate_release_playlist(artist_ids, start_date, end_date)
            mock_method.assert_called_with(artist_ids, mock.ANY, mock.ANY
                                           , start_date=start_date, end_date=end_date)
    
    @mock.patch('src.Spotify_Features.BackupSpotifyData')
    def test_backup_spotify_library(self, MockBackupSpotifyData):
        self.spotify_features.backup_spotify_library()
        MockBackupSpotifyData.return_value.backup_data.assert_called_once()

    @mock.patch('src.Spotify_Features.LogPlayback')
    @mock.patch('src.Spotify_Features.DatabaseHelpers')
    def test_log_playback_to_db(self, MockDatabaseHelpers, MockLogPlayback):
        mock_db_helpers = MockDatabaseHelpers.return_value
        mock_db_helpers.db_get_user_followed_artists.return_value = [{'name': 'Artist 1'}]
        playback = {'context': {'type': 'playlist', 'id': 'Pl002'}}
        
        # Test __ playlist That its not incremented
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, False)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test __ playlist that I don't follow to increment
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 2'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test Incorrect __ playlist
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '_Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test unknown playlist
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl001', 'name': '_Artist 1'}]
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test multiple artists, multiple playlists
        mock_db_helpers.db_get_user_followed_artists.return_value = [{'name': 'Artist 1'}
                                                                     , {'name': 'Artist 22'}
                                                                     , {'name': 'Artist 3'}]     
        mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'Pl002', 'name': '__Artist 1'}
                                                              , {'id': 'Pl003', 'name': 'EMPTY'}
                                                              , {'id': 'Pl004', 'name': '__Artist 3'}]
        playback = {'context': {'type': 'playlist', 'id': 'Pl004'}}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, False)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test None context
        playback = {'context': None}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        # Test non playlist context
        playback = {'context': {'type': 'album', 'id': 'Al002'}}
        self.spotify_features.log_playback_to_db(playback)
        MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)
        MockLogPlayback.return_value.log_track.reset_mock()
        
        

    # def test_generate_artist_playlist_from_playlist(self):
    #     playlist_id = 'test_playlist_id'
    #     self.mock_misc_features.get_first_artist_from_playlist.return_value = 'test_artist_id'
    #     self.spotify_features.generate_artist_playlist_from_playlist(playlist_id)
    #     self.mock_misc_features.get_first_artist_from_playlist.assert_called_once_with(playlist_id)
    #     self.mock_misc_features.generate_artist_release.assert_called_once_with(
    #         ['test_artist_id'], 'Test Artist GO THROUGH', 'Every Track by Test Artist'
    #     )

    # def test_generate_monthly_release(self):
    #     thelp.create_env(self.mock_spotify_helpers)
    #     self.mock_spotify_helpers.get_user_artists.return_value = [
    #         {'id': 'artist1', 'name': 'Artist One'},
    #         {'id': 'artist2', 'name': 'Artist Two'}
    #     ]
    #     self.spotify_features.generate_monthly_release()
    #     self.mock_misc_features.generate_artist_release.assert_called_once_with(
    #         ['artist1', 'artist2'],
    #         'Release Radar: 09-2023',
    #         'Releases From All Followed Artists From The Month 09-2023',
    #         start_date=datetime(2023, 9, 1),
    #         end_date=datetime(2023, 9, 30)
    #     )

    # def test_generate_release_playlist(self):
    #     artist_ids = ['artist1', 'artist2']
    #     start_date = datetime(2023, 1, 1)
    #     end_date = datetime(2023, 1, 31)
    #     self.spotify_features.generate_release_playlist(artist_ids, start_date, end_date)
    #     self.mock_misc_features.generate_artist_release.assert_called_once_with(
    #         artist_ids,
    #         'Release Radar: 01-01-2023 -> 01-31-2023',
    #         'Releases From *given* Artists From 01-01-2023 -> 01-31-2023',
    #         start_date=start_date,
    #         end_date=end_date
    #     )

    # def test_backup_spotify_library(self):
    #     with patch('src.Spotify_Features.BackupSpotifyData') as MockBackupSpotifyData:
    #         self.spotify_features.backup_spotify_library()
    #         MockBackupSpotifyData.return_value.backup_data.assert_called_once()

    # def test_log_playback_to_db(self):
    #     playback = {'context': {'type': 'playlist', 'id': 'test_playlist_id'}}
    #     with patch('src.Spotify_Features.DatabaseHelpers') as MockDatabaseHelpers:
    #         mock_db_helpers = MockDatabaseHelpers.return_value
    #         mock_db_helpers.db_get_user_playlists.return_value = [{'id': 'test_playlist_id', 'name': 'Test Playlist'}]
    #         mock_db_helpers.db_get_user_followed_artists.return_value = [{'name': 'Test Artist'}]
    #         with patch('src.Spotify_Features.LogPlayback') as MockLogPlayback:
    #             self.spotify_features.log_playback_to_db(playback)
    #             MockLogPlayback.return_value.log_track.assert_called_once_with(playback, True)

    # def test_shuffle_playlist(self):
    #     playlist_id = 'test_playlist_id'
    #     shuffle_type = ShuffleType.RANDOM
    #     with patch('src.Spotify_Features.Shuffler') as MockShuffler:
    #         self.spotify_features.shuffle_playlist(playlist_id, shuffle_type)
    #         MockShuffler.return_value.shuffle.assert_called_once_with(playlist_id, shuffle_type)

    # def test_distribute_tracks_to_collections(self):
    #     playlist_id = 'test_playlist_id'
    #     self.spotify_features.distribute_tracks_to_collections(playlist_id)
    #     self.mock_misc_features.distribute_tracks_to_collections_from_playlist.assert_called_once_with(playlist_id)

    # def test_organize_playlist_by_date(self):
    #     playlist_id = 'test_playlist_id'
    #     self.spotify_features.organize_playlist_by_date(playlist_id)
    #     self.mock_misc_features.reorganize_playlist.assert_called_once_with(playlist_id)

    # def test_get_playback_state(self):
    #     self.mock_spotify_helpers.get_playback_state.return_value = {'id': 'test_track_id', 'name': 'Test Track'}
    #     result = self.spotify_features.get_playback_state()
    #     self.assertEqual(result, {'id': 'test_track_id', 'name': 'Test Track'})

    # def test_update_daily_latest_playlist(self):
    #     self.spotify_features.update_daily_latest_playlist()
    #     self.mock_misc_features.update_daily_latest_playlist.assert_called_once()

    # def test_skip_track(self):
    #     self.spotify_features.skip_track()
    #     self.mock_spotify_helpers.change_playback.assert_called_once_with(skip="next")

    # def test_generate_weekly_report(self):
    #     with patch('src.Spotify_Features.SanityTest') as MockSanityTest:
    #         with patch('src.Spotify_Features.WeeklyReport') as MockWeeklyReport:
    #             self.spotify_features.generate_weekly_report()
    #             MockWeeklyReport.return_value.gen_weekly_report.assert_called_once()

    # def test_run_sanity_checks(self):
    #     with patch('src.Spotify_Features.SanityTest') as MockSanityTest:
    #         mock_sanity_tester = MockSanityTest.return_value
    #         self.spotify_features.run_sanity_checks()
    #         mock_sanity_tester.sanity_diffs_in_major_playlist_sets.assert_called_once()
    #         mock_sanity_tester.sanity_in_progress_artists.assert_called_once()
    #         mock_sanity_tester.sanity_duplicates.assert_called_once()
    #         mock_sanity_tester.sanity_artist_playlist_integrity.assert_called_once()
    #         mock_sanity_tester.sanity_contributing_artists.assert_called_once()

    # def test_upload_latest_backup_to_drive(self):
    #     with patch('src.Spotify_Features.glob') as MockGlob:
    #         MockGlob.return_value = ['/path/to/backup1', '/path/to/backup2']
    #         with patch('src.Spotify_Features.os.path.getmtime', side_effect=[1, 2]):
    #             with patch('src.Spotify_Features.DriveUploader') as MockDriveUploader:
    #                 self.spotify_features.upload_latest_backup_to_drive()
    #                 MockDriveUploader.return_value.upload_file.assert_called_once_with('/path/to/backup2')

    # def test_print_most_featured_artists(self):
    #     self.mock_misc_features.generate_featured_artists_list.return_value = [
    #         ('artist1', [1, 2, [('track1', 'Track 1')], 3]),
    #         ('artist2', [1, 1, [('track2', 'Track 2')], 2])
    #     ]
    #     with patch('builtins.print') as mock_print:
    #         self.spotify_features.print_most_featured_artists()
    #         mock_print.assert_called()