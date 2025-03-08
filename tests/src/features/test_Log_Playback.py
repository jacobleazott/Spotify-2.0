# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - LOG PLAYBACK                CREATED: 2024-10-11          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Log_Playback.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import sqlite3
import unittest

from datetime import datetime
from unittest import mock

import tests.helpers.api_response_test_messages as artm

from src.features.Log_Playback     import LogPlayback
from src.helpers.Settings          import Settings
from tests.helpers.mocked_Settings import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Log Playback functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestLogPlayback(unittest.TestCase):
    
    def test_init(self):
        log_playback = LogPlayback()
        self.assertEqual(log_playback.ldb_path, Settings.LISTENING_DB)
        self.assertEqual(log_playback.tcdb_path, Settings.TRACK_COUNTS_DB)
        
        log_playback = LogPlayback(ldb_path="/test/path/1", tcdb_path="/test/path/2")
        self.assertEqual(log_playback.ldb_path, "/test/path/1")
        self.assertEqual(log_playback.tcdb_path, "/test/path/2")
    
    def test_logger_default(self):
        log_playback = LogPlayback()
        self.assertEqual(log_playback.logger, logging.getLogger())

    def test_logger_custom(self):
        custom_logger = logging.getLogger('custom_logger')
        log_playback = LogPlayback(logger=custom_logger)
        self.assertEqual(log_playback.logger, custom_logger)
    
    def test_increment_play_count_db(self):
        shared_memory_db = "file:shared_memory?mode=memory&cache=shared"
        log_playback = LogPlayback(tcdb_path=shared_memory_db)
        conn = sqlite3.connect(shared_memory_db)
        # Test New Track.
        log_playback.track_id = "Tr001"
        log_playback.increment_play_count_db()
        self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 1)])
        # Test Updating Track.
        for _ in range(10):
            log_playback.increment_play_count_db()
        self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11)])
        # Test Lots of Calls.
        log_playback.track_id = "Tr002"
        for _ in range(99):
            log_playback.increment_play_count_db()
        self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11), ('Tr002', 99)])
        # Test Empty String Track ID.
        log_playback.track_id = ""
        for _ in range(2):
            log_playback.increment_play_count_db()
        self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11), ('Tr002', 99), ("", 2)])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('pickle.load')
    @mock.patch('pickle.dump')
    def test_update_last_track_count(self, mock_dump, mock_load, mock_open):
        # Create an instance of LogPlayback
        log_playback = LogPlayback()
        log_playback.track_id = 'Tr001'
        log_playback.increment_play_count_db = mock.MagicMock() # We don't care about triggering this here.

        # Test FileNotFoundError When Reading File.
        mock_load.side_effect = FileNotFoundError
        log_playback.update_last_track_count()
        mock_dump.assert_called_once_with(('Tr001', True), mock_open())
        
        # Test EOFError When Reading File.
        mock_load.side_effect = EOFError
        mock_dump.reset_mock()
        log_playback.update_last_track_count()
        mock_dump.assert_called_once_with(('Tr001', True), mock_open())
        
        # Must change side_effect to None, reset_mock() doesn't reset this.
        mock_load.side_effect = None

        # Test track ID is different.
        mock_dump.reset_mock()
        mock_load.return_value = ('Tr002', False)
        log_playback.update_last_track_count()
        mock_dump.assert_called_once_with(('Tr001', True), mock_open())

        # Test track ID is the same and value is True.
        mock_dump.reset_mock()
        mock_load.return_value = ('Tr001', True)
        
        log_playback.update_last_track_count()
        mock_dump.assert_called_once_with(('Tr001', False), mock_open())
        log_playback.increment_play_count_db.assert_called_once()
        
        # Test track ID is the same and value is False.
        mock_dump.reset_mock()
        log_playback.increment_play_count_db.reset_mock() 
        mock_load.return_value = ('Tr001', False)
        log_playback.update_last_track_count()
        mock_dump.assert_not_called()
        log_playback.increment_play_count_db.assert_not_called()
    
    @mock.patch('src.features.Log_Playback.Settings', Test_Settings)
    @mock.patch('src.features.Log_Playback.datetime')
    def test_log_track(self, mock_datetime):
        shared_memory_db = "file:shared_memory?mode=memory&cache=shared"
        log_playback = LogPlayback(ldb_path=shared_memory_db)
        conn = sqlite3.connect(shared_memory_db)
        log_playback.update_last_track_count = mock.MagicMock() # We don't care about triggering this here.
        playback = artm.get_playback_state_test_message.copy()
        
        # Test "Normal" Playback.
        playback['track']['id'] = "test_track_id"
        mock_datetime.now.return_value = datetime(2024, 10, 11, 12, 30, 0)
        log_playback.log_track(playback, False)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.assertIn(('2024',), tables)
        res = conn.execute("SELECT * FROM '2024';").fetchall()
        self.assertEqual(res, [('test_track_id', '2024-10-11 12:30:00')])
        log_playback.update_last_track_count.assert_not_called()

        # Test Different Year.
        mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0)
        log_playback.log_track(playback, True)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.assertIn(('2023',), tables)
        res = conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('test_track_id', '2023-01-01 00:00:00')])
        log_playback.update_last_track_count.assert_called_once()
        log_playback.update_last_track_count.reset_mock()

        # Test None Playback.
        log_playback.log_track(None, True) # Should not insert anything
        res = conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('test_track_id', '2023-01-01 00:00:00')])
        log_playback.update_last_track_count.assert_not_called()
        
        # Test Not Playing.
        playback['is_playing'] = False
        log_playback.log_track(playback, True) # Should not log anything
        res = conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('test_track_id', '2023-01-01 00:00:00')])
        log_playback.update_last_track_count.assert_not_called()
        playback['is_playing'] = True
        
        # Test MACRO track_id.
        Test_Settings.MACRO_LIST.append("test_macro_id")
        playback['track']['id'] = "test_macro_id"
        log_playback.log_track(playback, True) # Should not log anything
        res = conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('test_track_id', '2023-01-01 00:00:00')])
        log_playback.update_last_track_count.assert_not_called()
        
        # Test None track_id.
        playback['track']['id'] = None
        playback['track']['name'] = "test track 1"
        conn.execute("DELETE FROM '2023'")
        conn.commit()
        log_playback.log_track(playback, True)
        res = conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('local_track_test track 1', '2023-01-01 00:00:00')])
        log_playback.update_last_track_count.assert_called_once()
        

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════