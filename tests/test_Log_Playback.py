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
import sys
import unittest

from datetime import datetime, timedelta
from pprint import pprint
from unittest import mock
from unittest.mock import MagicMock

from Log_Playback import LogPlayback
from Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Log Playback functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestLogPlayback(unittest.TestCase):
    
    def test_increment_play_count_db(self):
        log_playback = LogPlayback(tcdb_path=":memory:")
        # Test New Track.
        log_playback.track_id = "Tr001"
        log_playback.increment_play_count_db()
        self.assertEqual(log_playback.tcdb_conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 1)])
        # Test Updating Track.
        for _ in range(10):
            log_playback.increment_play_count_db()
        self.assertEqual(log_playback.tcdb_conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11)])
        # Test Lots of Calls.
        log_playback.track_id = "Tr002"
        for _ in range(99):
            log_playback.increment_play_count_db()
        self.assertEqual(log_playback.tcdb_conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11), ('Tr002', 99)])
        # Test Empty String Track ID.
        log_playback.track_id = ""
        for _ in range(2):
            log_playback.increment_play_count_db()
        self.assertEqual(log_playback.tcdb_conn.execute(f"SELECT * FROM tracks").fetchall()
                         , [('Tr001', 11), ('Tr002', 99), ("", 2)])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('pickle.load')
    @mock.patch('pickle.dump')
    def test_update_last_track_count(self, mock_dump, mock_load, mock_open):
        # Create an instance of LogPlayback
        log_playback = LogPlayback()
        log_playback.track_id = 'Tr001'
        log_playback.increment_play_count_db = MagicMock() # We don't care about triggering this here.

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

    @mock.patch('Log_Playback.datetime')
    def test_log_track(self, mock_datetime):
        log_playback = LogPlayback(ldb_path=":memory:")
        log_playback.update_last_track_count = MagicMock() # We don't care about triggering this here.
        
        mock_datetime.now.return_value = datetime(2024, 10, 11, 12, 30, 0)
        log_playback.log_track('test_track_id', 'fake track name')
        tables = log_playback.ldb_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.assertIn(('2024',), tables)
        res = log_playback.ldb_conn.execute("SELECT * FROM '2024';").fetchall()
        self.assertEqual(res, [('test_track_id', '2024-10-11 12:30:00')])

        # Test for a different year.
        mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0)
        log_playback.log_track('track_2023_id', 'fake 2023 track name')
        tables = log_playback.ldb_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.assertIn(('2023',), tables)
        res = log_playback.ldb_conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('track_2023_id', '2023-01-01 00:00:00')])

        # Test an empty track_id.
        log_playback.log_track("", "")  # Should not insert anything
        res = log_playback.ldb_conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('track_2023_id', '2023-01-01 00:00:00')])
        
        # Test MACRO track_id.
        log_playback.log_track(Settings.MACRO_LIST[0], "macro track")  # Should not log anything
        cursor = log_playback.ldb_conn.cursor()
        res = log_playback.ldb_conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('track_2023_id', '2023-01-01 00:00:00')])

        # Test None as track_id.
        log_playback.ldb_conn.execute("DELETE FROM '2023'")
        log_playback.log_track(None, 'test track 1')
        res = log_playback.ldb_conn.execute("SELECT * FROM '2023';").fetchall()
        self.assertEqual(res, [('local_track_test track 1', '2023-01-01 00:00:00')])


    
    
# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════