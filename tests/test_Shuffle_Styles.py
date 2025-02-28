# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SHUFFLE STYLES              CREATED: 2024-10-11          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Shuffle_Styles.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import sqlite3
import unittest
from unittest import mock

from src.features.Shuffle_Styles   import Shuffler, ShuffleType
from tests.helpers.mocked_Settings import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Shuffle Styles functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Shuffle_Styles.Settings', Test_Settings)
class TestShuffler(unittest.TestCase):
    
    @mock.patch('src.features.Shuffle_Styles.DatabaseHelpers')
    @mock.patch('src.features.Shuffle_Styles.Settings', Test_Settings)
    def setUp(self, MockDatabaseHelpers):
        self.MockDatabaseHelpers = MockDatabaseHelpers
        self.mock_spotify = mock.MagicMock()
        self.shuffler = Shuffler(self.mock_spotify)

    def test_init(self):
        self.assertEqual(self.shuffler.spotify, self.mock_spotify)
        self.assertIsNone(self.shuffler.tcdb_conn)
        self.assertEqual(self.shuffler.tcdb_path, Test_Settings.TRACK_COUNTS_DB)
        self.MockDatabaseHelpers.assert_called_once_with(logger=self.shuffler.logger)
        self.assertEqual(self.shuffler.logger, logging.getLogger())
    
    def test_logger_custom(self):
        custom_logger = logging.getLogger('custom_logger')
        shuffler = Shuffler(self.mock_spotify, logger=custom_logger)
        self.assertEqual(shuffler.logger, custom_logger)
    
    def test_close(self):
        self.shuffler.tcdb_conn = sqlite3.connect(":memory:")
        self.shuffler.close()
        self.assertIsNone(self.shuffler.tcdb_conn)
        
        self.shuffler = Shuffler(self.mock_spotify)
        self.assertIsNone(self.shuffler.tcdb_conn)
        self.shuffler.close()
        self.assertIsNone(self.shuffler.tcdb_conn)

    @mock.patch("random.shuffle")
    def test_weighted_shuffle(self, mock_shuffle):
        self.shuffler.tcdb_conn = sqlite3.connect(":memory:")
        self.shuffler.tcdb_conn.execute(f'''CREATE TABLE IF NOT EXISTS 'tracks'(
                                     track_id TEXT PRIMARY KEY,
                                     play_count INTEGER NOT NULL);''')

        tracks = [
            ('track_1', 5),
            ('track_2', 3),
            ('track_3', 10),
            ('track_4', 1),
            ('track_5', 10),
            ('track_6', 10),
            ('track_7', 1),
        ]
        self.shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        
        # Test "Normal" Scenario.
        res = self.shuffler._weighted_shuffle(["track_1", "track_2", "track_3"])
        self.assertEqual(res, ["track_2", "track_1", "track_3"])
        self.assertEqual(mock_shuffle.call_count, 3) # Only 3 Groupings Of Different Play Counts.
        
        # Test Duplicate Tracks.
        mock_shuffle.reset_mock()
        res = self.shuffler._weighted_shuffle(["track_1", "track_2", "track_3", "track_4", "track_4"])
        self.assertEqual(res, ["track_4", "track_4", "track_2", "track_1", "track_3"])
        self.assertEqual(mock_shuffle.call_count, 4) # Only 4 Groupings Of Different Play Counts.
        
        # Test Play Count Groupings.
        mock_shuffle.reset_mock()
        res = self.shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, ["track_4", "track_7", "track_2", "track_1", "track_3", "track_5", "track_6"])
        self.assertEqual(mock_shuffle.call_count, 4) # Only 4 Groupings Of Different Play Counts.
        
        # Test Over Queeu Length.
        self.shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_{i}", f"{i}") for i in range(Test_Settings.MAX_QUEUE_LENGTH + 50)]
        self.shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = self.shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, [track[0] for track in tracks][:Test_Settings.MAX_QUEUE_LENGTH])
        self.assertEqual(mock_shuffle.call_count, Test_Settings.MAX_QUEUE_LENGTH+1) # 81 Groupings Of Different Play Counts From Loop.
        
        # Test Exact Queeu Length.
        self.shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_{i}", f"{i}") for i in range(Test_Settings.MAX_QUEUE_LENGTH)]
        self.shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = self.shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, [track[0] for track in tracks][:Test_Settings.MAX_QUEUE_LENGTH])
        self.assertEqual(mock_shuffle.call_count, Test_Settings.MAX_QUEUE_LENGTH)
        
        # Test Over Queue Length With Large Groupings.
        Test_Settings.MAX_QUEUE_LENGTH = 30
        self.shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_1_{i}", 10) for i in range(20)]
        tracks += [(f"track_2_{i}", 20) for i in range(20)]
        self.shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = self.shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(len(res), 40) # We Grab All Tracks With Same Play Count Over Queue Length.
        self.assertEqual(mock_shuffle.call_count, 2) # Only 2 Different Play Count Values
        
    def test_weighted_shuffle_no_connection(self):
        self.shuffler.tcdb_conn = None
        with mock.patch('sqlite3.connect', return_value=sqlite3.connect(":memory:")) as mock_connect:
            tracks = self.shuffler._weighted_shuffle(["track_1", "track_2", "track_3"])
            self.assertCountEqual(tracks, ["track_1", "track_2", "track_3"])
            mock_connect.assert_called_once_with(Test_Settings.TRACK_COUNTS_DB)
            
    
    @mock.patch('random.shuffle')
    @mock.patch.object(Shuffler, '_weighted_shuffle')
    def test_shuffle(self, mock_weighted_shuffle, mock_random_shuffle):
        # Mock return for method call to sim getting playlist tracks.
        self.shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': 'track_1', 'is_local': False}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': False}]

        # Test RANDOM shuffle.
        self.shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        self.shuffler.dbh.db_get_tracks_from_playlist.assert_called_once_with('some_playlist_id')
        mock_random_shuffle.assert_called_once_with(['track_1', 'track_2', 'track_3'])
        self.mock_spotify.write_to_queue.assert_any_call(['track_1'])

        # Test WEIGHTED shuffle.
        mock_weighted_shuffle.return_value = ['track_3', 'track_1', 'track_2']
        self.mock_spotify.reset_mock()
        self.shuffler.shuffle('some_playlist_id', ShuffleType.WEIGHTED)
        mock_weighted_shuffle.assert_called_once_with(['track_1', 'track_2', 'track_3'])
        self.mock_spotify.write_to_queue.assert_any_call(['track_3']) # Make sure proper track was sent to queue
        
        # Test MACRO_LIST isn't included.
        Test_Settings.MACRO_LIST.append("fake_macro_track")
        self.shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': "fake_macro_track", 'is_local': False}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': False}]
        mock_random_shuffle.reset_mock()
        self.mock_spotify.reset_mock()
        self.shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        mock_random_shuffle.assert_called_once_with(['track_2', 'track_3'])
        self.mock_spotify.write_to_queue.assert_any_call(['track_2'])
        self.mock_spotify.write_to_queue.assert_any_call(['track_3'])
        
        # Test local tracks aren't included.
        self.shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': "track_1", 'is_local': True}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': True}]
        mock_random_shuffle.reset_mock()
        self.mock_spotify.reset_mock()
        self.shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        mock_random_shuffle.assert_called_once_with(['track_2'])
        self.mock_spotify.write_to_queue.assert_any_call(['track_2'])

        # Test Unknown ShuffleType.
        with self.assertRaises(Exception): self.shuffler.shuffle('some_playlist_id', 'UNKNOWN_TYPE')
        
    def test_shuffle_no_tracks(self):
        self.shuffler.dbh.db_get_tracks_from_playlist.return_value = []
        self.shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        self.mock_spotify.write_to_queue.assert_not_called()
        self.mock_spotify.change_playback.assert_not_called()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════