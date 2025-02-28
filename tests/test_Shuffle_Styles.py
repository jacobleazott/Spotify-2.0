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
import sqlite3
import unittest
from unittest import mock

from src.features.Shuffle_Styles   import Shuffler, ShuffleType
from tests.helpers.mocked_Settings import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Shuffle Styles functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Shuffle_Styles.Settings', Test_Settings)
@mock.patch('src.features.Shuffle_Styles.DatabaseHelpers', mock.MagicMock())
class TestShuffler(unittest.TestCase):

    @mock.patch("random.shuffle")
    def test_weighted_shuffle(self, mock_shuffle):
        mock_spotify = mock.MagicMock()
        shuffler = Shuffler(mock_spotify)
        
        shuffler.tcdb_conn = sqlite3.connect(":memory:")
        shuffler.tcdb_conn.execute(f'''CREATE TABLE IF NOT EXISTS 'tracks'(
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
        shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        
        # Test "Normal" Scenario.
        res = shuffler._weighted_shuffle(["track_1", "track_2", "track_3"])
        self.assertEqual(res, ["track_2", "track_1", "track_3"])
        self.assertEqual(mock_shuffle.call_count, 3) # Only 3 Groupings Of Different Play Counts.
        
        # Test Duplicate Tracks.
        mock_shuffle.reset_mock()
        res = shuffler._weighted_shuffle(["track_1", "track_2", "track_3", "track_4", "track_4"])
        self.assertEqual(res, ["track_4", "track_4", "track_2", "track_1", "track_3"])
        self.assertEqual(mock_shuffle.call_count, 4) # Only 4 Groupings Of Different Play Counts.
        
        # Test Play Count Groupings.
        mock_shuffle.reset_mock()
        res = shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, ["track_4", "track_7", "track_2", "track_1", "track_3", "track_5", "track_6"])
        self.assertEqual(mock_shuffle.call_count, 4) # Only 4 Groupings Of Different Play Counts.
        
        # Test Over Queeu Length.
        shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_{i}", f"{i}") for i in range(Test_Settings.MAX_QUEUE_LENGTH + 50)]
        shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, [track[0] for track in tracks][:Test_Settings.MAX_QUEUE_LENGTH])
        self.assertEqual(mock_shuffle.call_count, Test_Settings.MAX_QUEUE_LENGTH+1) # 81 Groupings Of Different Play Counts From Loop.
        
        # Test Exact Queeu Length.
        shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_{i}", f"{i}") for i in range(Test_Settings.MAX_QUEUE_LENGTH)]
        shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(res, [track[0] for track in tracks][:Test_Settings.MAX_QUEUE_LENGTH])
        self.assertEqual(mock_shuffle.call_count, Test_Settings.MAX_QUEUE_LENGTH)
        
        # Test Over Queue Length With Large Groupings.
        Test_Settings.MAX_QUEUE_LENGTH = 30
        shuffler.tcdb_conn.execute("DELETE FROM tracks")
        tracks = [(f"track_1_{i}", 10) for i in range(20)]
        tracks += [(f"track_2_{i}", 20) for i in range(20)]
        shuffler.tcdb_conn.executemany('INSERT INTO tracks (track_id, play_count) VALUES (?, ?)', tracks)
        mock_shuffle.reset_mock()
        res = shuffler._weighted_shuffle([track[0] for track in tracks])
        self.assertEqual(len(res), 40) # We Grab All Tracks With Same Play Count Over Queue Length.
        self.assertEqual(mock_shuffle.call_count, 2) # Only 2 Different Play Count Values
    
    @mock.patch('random.shuffle')
    @mock.patch.object(Shuffler, '_weighted_shuffle')
    def test_shuffle(self, mock_weighted_shuffle, mock_random_shuffle):
        mock_spotify = mock.MagicMock() # No real need to even use our mocked spotipy here.
        shuffler = Shuffler(spotify=mock_spotify)

        # Mock return for method call to sim getting playlist tracks.
        shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': 'track_1', 'is_local': False}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': False}]

        # Test RANDOM shuffle.
        shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        shuffler.dbh.db_get_tracks_from_playlist.assert_called_once_with('some_playlist_id')
        mock_random_shuffle.assert_called_once_with(['track_1', 'track_2', 'track_3'])
        mock_spotify.write_to_queue.assert_any_call(['track_1'])

        # Test WEIGHTED shuffle.
        mock_weighted_shuffle.return_value = ['track_3', 'track_1', 'track_2']
        mock_spotify.reset_mock()
        shuffler.shuffle('some_playlist_id', ShuffleType.WEIGHTED)
        mock_weighted_shuffle.assert_called_once_with(['track_1', 'track_2', 'track_3'])
        mock_spotify.write_to_queue.assert_any_call(['track_3']) # Make sure proper track was sent to queue
        
        # Test MACRO_LIST isn't included.
        Test_Settings.MACRO_LIST.append("fake_macro_track")
        shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': "fake_macro_track", 'is_local': False}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': False}]
        mock_random_shuffle.reset_mock()
        mock_spotify.reset_mock()
        shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        mock_random_shuffle.assert_called_once_with(['track_2', 'track_3'])
        mock_spotify.write_to_queue.assert_any_call(['track_2'])
        mock_spotify.write_to_queue.assert_any_call(['track_3'])
        
        # Test local tracks aren't included.
        shuffler.dbh.db_get_tracks_from_playlist.return_value = [
              {'id': "track_1", 'is_local': True}
            , {'id': 'track_2', 'is_local': False}
            , {'id': 'track_3', 'is_local': True}]
        mock_random_shuffle.reset_mock()
        mock_spotify.reset_mock()
        shuffler.shuffle('some_playlist_id', ShuffleType.RANDOM)
        mock_random_shuffle.assert_called_once_with(['track_2'])
        mock_spotify.write_to_queue.assert_any_call(['track_2'])

        # Test Unknown ShuffleType.
        with self.assertRaises(Exception): shuffler.shuffle('some_playlist_id', 'UNKNOWN_TYPE')


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════