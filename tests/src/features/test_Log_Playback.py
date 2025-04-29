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
import uuid

from datetime import datetime
from unittest import mock

import tests.helpers.api_response_test_messages as artm

from src.features.Log_Playback     import LogPlayback
from src.helpers.Settings          import Settings
from tests.helpers.mocked_Settings import Test_Settings

Test_Settings.LISTENING_VAULT_DB = ":memory:"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Log Playback functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Log_Playback.Settings', Test_Settings)
class TestLogPlayback(unittest.TestCase):
    
    def test_init(self):
        log_playback = LogPlayback()
        self.assertEqual(log_playback.vault_db.db_path, Test_Settings.LISTENING_VAULT_DB)
        self.assertEqual(log_playback.logger, logging.getLogger())
        
        custom_logger = logging.getLogger('custom_logger')
        log_playback = LogPlayback(logger=custom_logger)
        self.assertEqual(log_playback.logger, custom_logger)

    # def test_increment_play_count_db(self):
    #     shared_memory_db = "file:shared_memory?mode=memory&cache=shared"
    #     log_playback = LogPlayback(tcdb_path=shared_memory_db)
    #     conn = sqlite3.connect(shared_memory_db)
    #     # Test New Track.
    #     log_playback.track_id = "Tr001"
    #     log_playback.increment_play_count_db()
    #     self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
    #                      , [('Tr001', 1)])
    #     # Test Updating Track.
    #     for _ in range(10):
    #         log_playback.increment_play_count_db()
    #     self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
    #                      , [('Tr001', 11)])
    #     # Test Lots of Calls.
    #     log_playback.track_id = "Tr002"
    #     for _ in range(99):
    #         log_playback.increment_play_count_db()
    #     self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
    #                      , [('Tr001', 11), ('Tr002', 99)])
    #     # Test Empty String Track ID.
    #     log_playback.track_id = ""
    #     for _ in range(2):
    #         log_playback.increment_play_count_db()
    #     self.assertEqual(conn.execute(f"SELECT * FROM tracks").fetchall()
    #                      , [('Tr001', 11), ('Tr002', 99), ("", 2)])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('pickle.load')
    @mock.patch('pickle.dump')
    def test_update_last_track_count(self, mock_dump, mock_load, mock_open):
        # Create an instance of LogPlayback
        log_playback = LogPlayback()
        log_playback.track['id'] = 'Tr001'
        log_playback.vault_db.increment_track_count = mock.MagicMock() # We don't care about triggering this here.

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
        log_playback.vault_db.increment_track_count.assert_called_once()
        
        # Test track ID is the same and value is False.
        mock_dump.reset_mock()
        log_playback.vault_db.increment_track_count.reset_mock() 
        mock_load.return_value = ('Tr001', False)
        log_playback.update_last_track_count()
        mock_dump.assert_not_called()
        log_playback.vault_db.increment_track_count.assert_not_called()
    
    def test_log_track(self):
        log_playback = LogPlayback()
        log_playback.vault_db = mock.MagicMock()
        log_playback.update_last_track_count = mock.MagicMock()
        test_playback = artm.get_playback_state_test_message.copy()
        test_playback['track']['id'] = "test_track_id"
        
        # Test None Playback
        log_playback.log_track(None, False)
        log_playback.vault_db.add_listening_session.assert_not_called()
        
        # Test Not Playing Playback.
        test_playback['is_playing'] = False
        log_playback.log_track(test_playback, False)
        log_playback.vault_db.add_listening_session.assert_not_called()
        test_playback['is_playing'] = True
        
        # Test Macro Track Playback.
        test_playback['track']['id'] = Test_Settings.MACRO_LIST[0]
        log_playback.log_track(test_playback, False)
        log_playback.vault_db.add_listening_session.assert_not_called()
        test_playback['track']['id'] = "test_track_id"
        
        # Test Local Track Playback.
        test_playback['track']['is_local'] = True
        test_playback['track']['id'] = None
        log_playback.log_track(test_playback, False)
        log_playback.vault_db.insert_many.assert_called()
        log_playback.vault_db.add_listening_session.assert_called_once_with("local_track_Fake Track 0")
        log_playback.update_last_track_count.assert_not_called()
        test_playback['track']['is_local'] = False
        test_playback['track']['id'] = "test_track_id"
        log_playback.vault_db.reset_mock()
        
        # Test Inc Track Count.
        log_playback.log_track(test_playback, True)
        log_playback.vault_db.insert_many.assert_called()
        log_playback.update_last_track_count.assert_called()
        log_playback.vault_db.add_listening_session.assert_called_once_with("test_track_id")
        log_playback.vault_db.reset_mock()
        
        # Test New Track Id.
        test_playback['track']['id'] = "new_track_id"
        log_playback.log_track(test_playback, False)
        log_playback.vault_db.insert_many.assert_called()
        log_playback.vault_db.add_listening_session.assert_called_once_with("new_track_id")
        log_playback.vault_db.reset_mock()
        

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════