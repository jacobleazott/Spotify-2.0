# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SANITY TESTS                CREATED: 2025-03-07          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Sanity_Tests.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import unittest

from unittest import mock

from src.features.Sanity_Tests import SanityTest
from src.helpers.Settings      import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Shuffle Styles functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestSanityTests(unittest.TestCase):
    @mock.patch('src.features.Sanity_Tests.SanityTest._gather_playlist_data')
    def setUp(self, mock_gather_playlist_data):
        self.sanityTester = SanityTest()
        print(self.sanityTester.track_list_to_disregard)
        print(list(Settings.MACRO_LIST))
    
    @mock.patch('src.features.Sanity_Tests.SanityTest._gather_playlist_data')
    def test_init(self, mock_gather_playlist_data):
        print(self.sanityTester.track_list_to_disregard)
        print(list(Settings.MACRO_LIST))
        self.assertEqual(self.sanityTester.logger, logging.getLogger())
        self.assertCountEqual(self.sanityTester.track_list_to_disregard, list(Settings.MACRO_LIST))
        
        custom_logger = logging.getLogger('custom_logger')
        custom_tester = SanityTest(logger=custom_logger)
        self.assertEqual(custom_tester.logger, custom_logger)
        self.assertEqual(mock_gather_playlist_data.call_count, 1)
    
    def test_gather_playlist_data(self):
        mock_dbh = mock.MagicMock()
        self.sanityTester.dbh = mock_dbh
        
        mock_dbh.db_get_user_playlists.return_value = [
            {'id': 'playlist_1', 'name': '__Test Artist 1'}
          , {'id': 'playlist_2', 'name': '__Test Artist 2'}
          , {'id': 'playlist_3', 'name': '_Test Artist 3'}
          , {'id': 'playlist_4', 'name': '2025'}
          , {'id': 'playlist_5', 'name': '2105'}
          , {'id': Settings.MASTER_MIX_ID, 'name': 'Master Mix'}
          , {'id': Settings.PLAYLIST_IDS_NOT_IN_ARTISTS[0], 'name': 'Not in Artists'}
        ]
        
        mock_playlist_data = {
            'playlist_1': [{'id': '1', 'name': 'Track 1', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}],
            'playlist_2': [{'id': '2', 'name': 'Track 2', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}],
            'playlist_3': [],
            'playlist_4': [{'id': '3', 'name': 'Track 3', 'duration_ms': 99, 'is_local': 1, 'is_playable': 0}],
            'playlist_5': [{'id': '4', 'name': 'Track 4', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}],
            Settings.MASTER_MIX_ID: 
                [{'id': '5', 'name': 'Track 5', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}],
            Settings.PLAYLIST_IDS_NOT_IN_ARTISTS[0]: 
                [{'id': '6', 'name': 'Track 6', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}],
        }
        
        mock_dbh.db_get_tracks_from_playlist.side_effect = lambda playlist_id: mock_playlist_data.get(playlist_id, [])
        self.sanityTester._gather_playlist_data()
        
        mock_dbh.db_get_user_followed_artists.assert_called_once()
        mock_dbh.db_get_user_playlists.assert_called_once()
        self.assertEqual(self.sanityTester.user_followed_artists, mock_dbh.db_get_user_followed_artists.return_value)
        self.assertEqual(self.sanityTester.user_playlists, mock_dbh.db_get_user_playlists.return_value)
        
        self.assertEqual(self.sanityTester.individual_artist_playlists, [
            {'name': 'Test Artist 1', 'tracks': mock_playlist_data['playlist_1']},
            {'name': 'Test Artist 2', 'tracks': mock_playlist_data['playlist_2']}])

        self.assertEqual(self.sanityTester.years_playlists, [
            {'name': '2025', 'tracks': mock_playlist_data['playlist_4']}])

        self.assertEqual(self.sanityTester.master_playlist, [
            {'name': 'Master Mix', 'tracks': mock_playlist_data[Settings.MASTER_MIX_ID]}])
        
        self.assertCountEqual(self.sanityTester.track_list_to_disregard, list(Settings.MACRO_LIST) + ['6'])
    
    def test_find_duplicates(self):
        pass
    
    def test_compare_track_lists(self):
        pass
    
    def test_sanity_diffs_in_major_playlist_sets(self):
        pass
    
    def test_sanity_in_progress_artists(self):
        pass
    
    def test_sanity_duplicates(self):
        pass
    
    def test_sanity_contributing_artists(self):
        pass
    
    def test_sanity_artist_playlist_integrity(self):
        pass
    
    def test_sanity_playable_tracks(self):
        pass


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════