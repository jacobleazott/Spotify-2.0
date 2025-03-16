# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - IMPLEMENTATIONS             CREATED: 2025-03-16          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Implementations.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import sqlite3
import threading
import time
import unittest

from datetime                          import datetime, timedelta
from unittest import mock

import src.Implementations
from src.Implementations           import *
from src.Spotify_Features          import SpotifyFeatures
from tests.helpers.mocked_Settings import Test_Settings


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Implementations functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.Implementations.Settings', Test_Settings)
class TestStatistics(unittest.TestCase):

    def setUp(self):
        src.Implementations.threads = []
        pass
    
    @mock.patch("src.Implementations.datetime")
    @mock.patch("src.Implementations.os")
    @mock.patch("src.Implementations.time")
    def test_monitor_script_runtime(self, mock_time, mock_os, mock_datetime):
        # Simulate start time
        start_time = datetime(2025, 3, 16)
        mock_datetime.now.side_effect = [
            start_time
          , start_time + timedelta(minutes=Test_Settings.MAX_RUNTIME_MINUTES + 1)  # Triggers exit
          , start_time
          , start_time 
          , start_time + timedelta(minutes=Test_Settings.MAX_RUNTIME_MINUTES + 1)  # Triggers exit
        ]

        # Test Immediate Exit
        mock_os._exit.side_effect = SystemExit("")
        with self.assertRaises(SystemExit):
            monitor_script_runtime()

        mock_os._exit.assert_called_once_with(1)
        mock_time.sleep.assert_not_called()
        mock_os.reset_mock()
        
        # Test Sleep
        with self.assertRaises(SystemExit):
            monitor_script_runtime()

        mock_os._exit.assert_called_once_with(1)
        mock_time.sleep.assert_called_once_with(60)
    
    @mock.patch("src.Implementations.threading")
    @mock.patch("src.Implementations.SpotifyFeatures")
    def test_startup_feature_thread(self, mock_spotify_features, mock_threading):
        mock_thread = mock.MagicMock()
        mock_threading.Thread.return_value = mock_thread
        
        def test_method():
            pass
        
        # Test Default
        startup_feature_thread(test_method)
        
        mock_spotify_features.assert_called_once_with(log_file_name="Default.log")
        mock_threading.Thread.assert_called_once_with(target=mock.ANY, args=(), kwargs={}, daemon=True)
        mock_thread.start.assert_called_once()
        mock_thread.join.assert_not_called()
        self.assertEqual(src.Implementations.threads, [mock_thread])
        mock_threading.Thread.reset_mock()
        mock_spotify_features.reset_mock()
        
        # Test Args and Kwargs
        startup_feature_thread(test_method, 1, 2, test='yep', test2='yepp')
        mock_threading.Thread.assert_called_once_with(target=mock.ANY
                                                      , args=(1, 2)
                                                      , kwargs={'test': 'yep', 'test2': 'yepp'}
                                                      , daemon=True)
        self.assertEqual(src.Implementations.threads, [mock_thread, mock_thread])
        mock_threading.Thread.reset_mock()
        mock_spotify_features.reset_mock()
        
        # Test log_file_name
        startup_feature_thread(test_method, log_file_name="Test.log")
        mock_spotify_features.assert_called_once_with(log_file_name="Test.log")
        self.assertEqual(src.Implementations.threads, [mock_thread, mock_thread, mock_thread])
        mock_spotify_features.reset_mock()
        
        # Test 'run_parallel'
        startup_feature_thread(test_method, run_parallel=False)
        mock_thread.join.assert_called_once()
        self.assertEqual(src.Implementations.threads, [mock_thread, mock_thread, mock_thread])

    def test_check_date_time(self):
        test_time = datetime(2025, 3, 11, 12, 30)
        # Test Hour and Minute Missing
        self.assertFalse(check_date_time(test_time))
        self.assertFalse(check_date_time(test_time, hour=12))
        self.assertFalse(check_date_time(test_time, minute=30))
        
        # Test Daily Trigger
        self.assertFalse(check_date_time(test_time, hour=12, minute=29))
        self.assertTrue(check_date_time(test_time, hour=12, minute=30))
        self.assertFalse(check_date_time(test_time, hour=12, minute=31))
        self.assertFalse(check_date_time(test_time, hour=11, minute=30))
        
        self.assertTrue(check_date_time(datetime(2025, 3, 11, 0, 0), hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 4, 11, 1, 0), hour=1, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 4, 30, 0, 2), hour=0, minute=2))
        self.assertTrue(check_date_time(datetime(2025, 12, 31, 23, 59), hour=23, minute=59))
        
        # Test Weekly Trigger
        self.assertTrue(check_date_time(datetime(2025, 3, 18, 0, 0), weekday=1, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 3, 17, 0, 0), weekday=0, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 3, 17, 0, 0), weekday=1, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 3, 17, 0, 0), weekday=0, hour=1, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 3, 17, 0, 0), weekday=0, hour=0, minute=1))
        self.assertFalse(check_date_time(datetime(2025, 3, 18, 0, 0), weekday=0, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 3, 16, 0, 0), weekday=0, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2024, 3, 17, 0, 0), weekday=0, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 4, 17, 0, 0), weekday=0, hour=0, minute=0))
        
        # Test Monthly Trigger
        self.assertTrue(check_date_time(datetime(2025, 4, 1, 0, 0), day=1, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 5, 1, 0, 0), day=1, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2030, 6, 1, 0, 0), day=1, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 4, 17, 0, 0), day=1, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 4, 2, 0, 0), day=1, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 1, 2, 0, 0), day=1, hour=0, minute=0))
        
        # Test Multiple Triggers
        self.assertTrue(check_date_time(datetime(2025, 3, 16, 0, 0), weekday=0, day=16, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 3, 16, 0, 0), weekday=6, day=1, hour=0, minute=0))
        self.assertFalse(check_date_time(datetime(2025, 3, 16, 0, 0), weekday=1, day=1, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 3, 1, 0, 0), weekday=0, day=1, hour=0, minute=0))
        self.assertTrue(check_date_time(datetime(2025, 3, 3, 0, 0), weekday=0, day=1, hour=0, minute=0))
    
    @mock.patch('src.Implementations.startup_feature_thread')
    def test_log_and_macro(self, mock_startup):
        mock_features = mock.MagicMock()
        
        def reset_mocks():
            mock_features.reset_mock()
            mock_startup.reset_mock()
        
        test_playback = {'context': {'type': 'playlist', 'id': 'Pl001'}, 'repeat_state': 'off'
                         , 'shuffle_state': False, 'track': {'id': 'Tr001'}}
        
        # Test None Playback
        mock_features.get_playback_state.return_value = None
        log_and_macro(mock_features)
        mock_features.get_playback_state.assert_called_once()
        mock_features.log_playback_to_db.assert_not_called()
        mock_startup.assert_not_called()
        reset_mocks()

        # Test None Context
        mock_features.get_playback_state.return_value = {'context': None}
        log_and_macro(mock_features)
        mock_features.log_playback_to_db.assert_called_once_with({'context': None})
        mock_startup.assert_not_called()
        reset_mocks()
        
        # Test None Playlist Context
        mock_features.get_playback_state.return_value = {'context': {'type': 'podcast'}}
        log_and_macro(mock_features)
        mock_features.log_playback_to_db.assert_called_once_with({'context': {'type': 'podcast'}})
        mock_startup.assert_not_called()
        reset_mocks()
        
        # Test Invalid Context
        with self.assertRaises(KeyError):
            mock_features.get_playback_state.return_value = {'context': {'type': 'playlist'}}
            log_and_macro(mock_features)
        reset_mocks()
        
        # Test No Macro Playback
        mock_features.get_playback_state.return_value = test_playback
        log_and_macro(mock_features)
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        mock_startup.assert_not_called()
        reset_mocks()
        
        # Test Generate Artist Macro
        test_playback['track']['id'] = Test_Settings.GEN_ARTIST_MACRO_ID
        log_and_macro(mock_features)
        mock_features.skip_track.assert_called_once()
        mock_startup.assert_called_once_with(SpotifyFeatures.generate_artist_playlist_from_playlist
                                             , test_playback['context']['id']
                                             , log_file_name="Generate-Artist-Playlist.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
        
        # Test Distribute Tracks Macro
        test_playback['track']['id'] = Test_Settings.DISTRIBUTE_TRACKS_MACRO_ID
        log_and_macro(mock_features)
        mock_features.skip_track.assert_called_once()
        mock_startup.assert_called_once_with(SpotifyFeatures.distribute_tracks_to_collections
                                             , test_playback['context']['id']
                                             , log_file_name="Distribute-Tracks.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
        
        # Test Organize Playlist Macro
        test_playback['track']['id'] = Test_Settings.ORGANIZE_PLAYLIST_MACRO_ID
        log_and_macro(mock_features)
        mock_features.skip_track.assert_called_once()
        mock_startup.assert_called_once_with(SpotifyFeatures.organize_playlist_by_date
                                             , test_playback['context']['id']
                                             , log_file_name="Organize-Playlist.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
        
        # Test Shuffle Macro
        test_playback['track']['id'] = "Tr001"
        test_playback['shuffle_state'] = True
        test_playback['repeat_state'] = "don't care"
        log_and_macro(mock_features)
        mock_features.skip_track.assert_not_called()
        mock_features.set_repeat_state.assert_called_once_with('off')
        mock_startup.assert_called_once_with(SpotifyFeatures.shuffle_playlist
                                             , test_playback['context']['id']
                                             , shuffle_type=ShuffleType.WEIGHTED
                                             , log_file_name="Shuffle-Playlist.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
        
        # Test Shuffle Styles
        test_playback['shuffle_state'] = False
        log_and_macro(mock_features)
        mock_features.skip_track.assert_not_called()
        mock_features.set_repeat_state.assert_called_once_with('off')
        mock_startup.assert_called_once_with(SpotifyFeatures.shuffle_playlist
                                             , test_playback['context']['id']
                                             , shuffle_type=ShuffleType.RANDOM
                                             , log_file_name="Shuffle-Playlist.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
        
        # Test Shuffle and Other Macro - Shuffle Takes Precedence, Only One Trigger
        test_playback['track']['id'] = Test_Settings.GEN_ARTIST_MACRO_ID
        log_and_macro(mock_features)
        mock_features.skip_track.assert_not_called()
        mock_features.set_repeat_state.assert_called_once_with('off')
        mock_startup.assert_called_once_with(SpotifyFeatures.shuffle_playlist
                                             , test_playback['context']['id']
                                             , shuffle_type=ShuffleType.RANDOM
                                             , log_file_name="Shuffle-Playlist.log")
        mock_features.log_playback_to_db.assert_called_once_with(test_playback)
        reset_mocks()
    
    @mock.patch('src.Implementations.SpotifyFeatures')
    @mock.patch('src.Implementations.startup_feature_thread')
    @mock.patch('src.Implementations.BackgroundScheduler')
    @mock.patch('src.Implementations.datetime')
    @mock.patch('src.Implementations.threading')
    @mock.patch('src.Implementations.time')
    def test_main(self, mock_time, mock_threading, mock_datetime, mock_scheduler, mock_startup, mock_features):
        global threads
        mock_thread = mock.MagicMock()
        mock_threading.Thread.return_value = mock_thread
        
        # Test Scheduler, Thread, and Time. No Triggers
        mock_datetime.now.return_value = datetime(2025, 3, 16, 23, 59, 59)
        main()
        
        mock_threading.Thread.assert_called_once_with(target=monitor_script_runtime, daemon=True)
        mock_thread.start.assert_called_once()
        mock_features.assert_called_once_with(log_file_name=mock.ANY)
        mock_scheduler.return_value.add_job.assert_called_once_with(log_and_macro
                                                            , mock.ANY
                                                            , args=[mock_features.return_value]
                                                            , next_run_time=mock_datetime.now.return_value)
        mock_scheduler.return_value.start.assert_called_once()
        mock_time.sleep.assert_has_calls([mock.call(45), mock.call(1)])
        mock_scheduler.return_value.shutdown.assert_called_once()
        
        # Test Joining Threads
        mock_1 = mock.MagicMock()
        mock_2 = mock.MagicMock()
        src.Implementations.threads += [mock_1, mock_2, mock_1]
        main()
        mock_2.join.assert_called_once()
        self.assertEqual(mock_1.join.call_count, 2)
        
        # Test Backup and Update Latest Playlist
        mock_datetime.now.return_value = datetime(2025, 3, 16, 2, 0, 30)
        main()
        mock_startup.assert_has_calls([
            mock.call(mock_features.backup_spotify_library
                      , log_file_name="Backup-Library.log"
                      , run_parallel=False)
          , mock.call(mock_features.update_daily_latest_playlist
                      , log_file_name="Update-Latest-Playlist.log"
                      , run_parallel=False)
        ])
        mock_startup.reset_mock()
        
        # Test Weekly Report
        mock_datetime.now.return_value = datetime(2025, 3, 17, 3, 0, 0)
        main()
        mock_startup.assert_called_once_with(mock_features.generate_weekly_report
                                             , log_file_name="Weekly-Report.log"
                                             , run_parallel=False)
        mock_startup.reset_mock()
        
        # Test Google Drive Upload
        mock_datetime.now.return_value = datetime(2025, 3, 16, 2, 0, 0)
        main()
        mock_startup.assert_any_call(mock_features.upload_latest_backup_to_drive
                                             , log_file_name="Drive-Upload.log"
                                             , run_parallel=False)
        self.assertEqual(mock_startup.call_count, 3) # 2AM Also Triggers Backup and Update Latest Playlist
        mock_startup.reset_mock()
        
        mock_datetime.now.return_value = datetime(2025, 3, 19, 2, 0, 0)
        main()
        mock_startup.assert_any_call(mock_features.upload_latest_backup_to_drive
                                             , log_file_name="Drive-Upload.log"
                                             , run_parallel=False)
        self.assertEqual(mock_startup.call_count, 3) # 2AM Also Triggers Backup and Update Latest Playlist
        mock_startup.reset_mock()
        
        # Test Monthly Release
        mock_datetime.now.return_value = datetime(2025, 4, 1, 1, 0, 59)
        main()
        mock_startup.assert_called_once_with(mock_features.generate_monthly_release
                                             , log_file_name="Monthly-Release.log"
                                             , run_parallel=False)
        mock_startup.reset_mock()


# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════