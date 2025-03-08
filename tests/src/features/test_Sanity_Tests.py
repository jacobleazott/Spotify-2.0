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
        self.mock_dbh = mock.MagicMock()
        self.sanityTester.dbh = self.mock_dbh
    
    @mock.patch('src.features.Sanity_Tests.SanityTest._gather_playlist_data')
    def test_init(self, mock_gather_playlist_data):
        self.assertEqual(self.sanityTester.logger, logging.getLogger())
        self.assertCountEqual(self.sanityTester.track_list_to_disregard, list(Settings.MACRO_LIST))
        
        custom_logger = logging.getLogger('custom_logger')
        custom_tester = SanityTest(logger=custom_logger)
        self.assertEqual(custom_tester.logger, custom_logger)
        self.assertEqual(mock_gather_playlist_data.call_count, 1)
    
    def test_gather_playlist_data(self):
        self.mock_dbh.db_get_user_playlists.return_value = [
            {'id': 'playlist_1', 'name': '__Test Artist 1'}
          , {'id': 'playlist_2', 'name': '__Test Artist 2'}
          , {'id': 'playlist_3', 'name': '_Test Artist 3'}
          , {'id': 'playlist_4', 'name': '2025'}
          , {'id': 'playlist_5', 'name': '2105'}
          , {'id': Settings.MASTER_MIX_ID, 'name': 'Master Mix'}
          , {'id': Settings.PLAYLIST_IDS_NOT_IN_ARTISTS[0], 'name': 'Not in Artists'}
        ]
        
        mock_playlist_data = {
            'playlist_1': [{'id': '1', 'name': 'Track 1', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}]
          , 'playlist_2': [{'id': '2', 'name': 'Track 2', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}]
          , 'playlist_3': []
          , 'playlist_4': [{'id': '3', 'name': 'Track 3', 'duration_ms': 99, 'is_local': 1, 'is_playable': 0}]
          , 'playlist_5': [{'id': '4', 'name': 'Track 4', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}]
          , Settings.MASTER_MIX_ID: 
                [{'id': '5', 'name': 'Track 5', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}]
          , Settings.PLAYLIST_IDS_NOT_IN_ARTISTS[0]: 
                [{'id': '6', 'name': 'Track 6', 'duration_ms': 10, 'is_local': 0, 'is_playable': 1}]
        }
        
        self.mock_dbh.db_get_tracks_from_playlist.side_effect = lambda playlist_id: \
            mock_playlist_data.get(playlist_id, [])
        self.sanityTester._gather_playlist_data()
        
        self.mock_dbh.db_get_user_followed_artists.assert_called_once()
        self.assertEqual(self.sanityTester.user_followed_artists
                         , self.mock_dbh.db_get_user_followed_artists.return_value)
        self.mock_dbh.db_get_user_playlists.assert_called_once()
        self.assertEqual(self.sanityTester.user_playlists, self.mock_dbh.db_get_user_playlists.return_value)
        
        self.assertEqual(self.sanityTester.individual_artist_playlists, [
            {'name': 'Test Artist 1', 'tracks': mock_playlist_data['playlist_1']},
            {'name': 'Test Artist 2', 'tracks': mock_playlist_data['playlist_2']}])

        self.assertEqual(self.sanityTester.years_playlists, [
            {'name': '2025', 'tracks': mock_playlist_data['playlist_4']}])

        self.assertEqual(self.sanityTester.master_playlist, [
            {'name': 'Master Mix', 'tracks': mock_playlist_data[Settings.MASTER_MIX_ID]}])
        
        self.assertCountEqual(self.sanityTester.track_list_to_disregard, list(Settings.MACRO_LIST) + ['6'])
    
    def test_find_duplicates(self):
        mock_track_artists = {
            '1': [{'name': 'Artist 2'}, {'name': 'Artist 1'}]
          , '2': [{'name': 'Artist 2'}, {'name': 'Artist 3'}]
          , '3': [{'name': 'Artist 3'}]
        }

        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: mock_track_artists.get(track_id, [])
        
        # Test Empty List
        duplicates = self.sanityTester._find_duplicates([])
        self.assertEqual(duplicates, [])
        
        # Test No Duplicates
        duplicates = self.sanityTester._find_duplicates([
            {'id': '1', 'name': 'Track 1'}
          , {'id': '2', 'name': 'Track 2'}
          , {'id': '3', 'name': 'Track 3'}
        ])
        self.assertEqual(duplicates, [])
        
        # Test Single Dupelicate
        duplicates = self.sanityTester._find_duplicates([
            {'id': '2', 'name': 'Track 2'}
          , {'id': '1', 'name': 'Track 1'}
          , {'id': '2', 'name': 'Track 2'}
          , {'id': '2', 'name': 'Track 2'}
          , {'id': '2', 'name': 'Track 2'}
        ])
        self.assertCountEqual(duplicates, [{'Track': 'Track 2', 'Artists': ['Artist 2', 'Artist 3']}])
        
        # Test Multiple Duplicates
        duplicates = self.sanityTester._find_duplicates([
            {'id': '2', 'name': 'Track 2'}
          , {'id': '1', 'name': 'Track 1'}
          , {'id': '1', 'name': 'Track 1'}
          , {'id': '2', 'name': 'Track 2'}
          , {'id': '3', 'name': 'Track 3'}
          , {'id': '4', 'name': 'Track 2'}
        ])
        self.assertCountEqual(duplicates, [{'Track': 'Track 2', 'Artists': ['Artist 2', 'Artist 3']}
                                         , {'Track': 'Track 1', 'Artists': ['Artist 2', 'Artist 1']}])
    
    def test_compare_track_lists(self):
        mock_track_artists = {
            '1': [{'name': 'Artist 1'}, {'name': 'Artist 2'}]
          , '2': [{'name': 'Artist 2'}]
          , Settings.MACRO_LIST[0]: [{'name': 'Artist 6'}]
        }

        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: mock_track_artists.get(track_id, [])
        
        # Test Empty Lists
        diff_list = self.sanityTester._compare_track_lists([], [])
        self.assertEqual(diff_list, [])
        
        # Test Empty Verify List
        diff_list = self.sanityTester._compare_track_lists([{'id': '1', 'name': 'Track 1'}], [])
        self.assertEqual(diff_list, [{"Track": "Track 1", "Artists": ['Artist 1', 'Artist 2']}])
        
        # Test Empty Key List
        diff_list = self.sanityTester._compare_track_lists([], [{'id': '1', 'name': 'Track 1'}])
        self.assertEqual(diff_list, [])
        
        # Test Disregard Tracks
        diff_list = self.sanityTester._compare_track_lists(
            [{'id': '1', 'name': 'Track 1'}, {'id': Settings.MACRO_LIST[0], 'name': 'Track 2'}]
            , [], disregard_tracks=True)
        self.assertEqual(diff_list, [{"Track": "Track 1", "Artists": ['Artist 1', 'Artist 2']}])
        
        # Test Disregard Tracks But Don't Set 'disregard_tracks
        diff_list = self.sanityTester._compare_track_lists([{'id': Settings.MACRO_LIST[0], 'name': 'Track 2'}], [])
        self.assertEqual(diff_list, [{"Track": "Track 2", "Artists": ['Artist 6']}])
        
        # Test Track Exists In Both
        diff_list = self.sanityTester._compare_track_lists([{'id': '1', 'name': 'Track 1'}
                                                            , {'id': '2', 'name': 'Track 2'}]
                                                         , [{'id': '2', 'name': 'Track 2'}])
        self.assertEqual(diff_list, [{"Track": "Track 1", "Artists": ['Artist 1', 'Artist 2']}])
    
    def test_sanity_diffs_in_major_playlist_sets(self):
        pass
    
    def test_sanity_in_progress_artists(self):
        pass
    
    @mock.patch('src.features.Sanity_Tests.SanityTest._find_duplicates')
    def test_sanity_duplicates(self, mock_find_duplicates):
        self.sanityTester.individual_artist_playlists = [{'name': 'Artist 1', 'tracks': ["test1"]}]
        self.sanityTester.years_playlists = [{'name': '2024', 'tracks': ["test2"]}
                                             , {'name': '2025', 'tracks': ["test3"]}]
        self.sanityTester.master_playlist = [{'name': 'Master', 'tracks': ["test4"]}]
        
        # Verify Find Duplicates is called for collections
        self.sanityTester.sanity_duplicates()
        mock_find_duplicates.assert_has_call(["test1"])
        mock_find_duplicates.assert_has_call(["test2"])
        mock_find_duplicates.assert_has_call(["test3"])
        mock_find_duplicates.assert_has_call(["test4"])
        mock_find_duplicates.assert_has_call(["test2", "test3"])
        self.assertEqual(mock_find_duplicates.call_count, 5)
        
    
    
    def test_sanity_contributing_artists(self):
        self.sanityTester.user_followed_artists = [{'name': 'Artist 1'}, {'name': 'Artist 2'}, {'name': 'Artist 3'}]
        self.sanityTester.individual_artist_playlists = [
            {'name': 'Artist 1', 'tracks': [
                {'id': '1', 'name': 'Track 1'}
              , {'id': '2', 'name': 'Track 2'}]}
          , {'name': 'Artist 2', 'tracks': [
                {'id': '3', 'name': 'Track 3'}]}
          , {'name': 'Artist 3', 'tracks': [
                {'id': '3', 'name': 'Track 3'}
              , {'id': '1', 'name': 'Track 1'}]}
          , {'name': 'Artist 4', 'tracks': []}
        ]
        
        mock_track_artists = {
            '1': [{'name': 'Artist 2'}, {'name': 'Artist 1'}, {'name': 'Artist 5'}]
          , '2': [{'name': 'Artist 2'}, {'name': 'Artist 3'}]
          , '3': [{'name': 'Artist 3'}]
        }

        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: mock_track_artists.get(track_id, [])
        
        sanity_artists = self.sanityTester.sanity_contributing_artists()
        for x in sanity_artists:
            print(x)
            
        self.assertEqual(sanity_artists, [
            {'Track': 'Track 1', 'Artists': ['Artist 2', 'Artist 1', 'Artist 5'], 'Missing': ['Artist 2']}
          , {'Track': 'Track 2', 'Artists': ['Artist 2', 'Artist 3'], 'Missing': ['Artist 2', 'Artist 3']}
        ])
    
    def test_sanity_artist_playlist_integrity(self):
        self.sanityTester.individual_artist_playlists = [
            {'name': 'Artist 1', 'tracks': [
                {'id': '1', 'name': 'Track 1'}
              , {'id': '2', 'name': 'Track 2'}]}
          , {'name': 'Artist 2', 'tracks': [
                {'id': '3', 'name': 'Track 3'}]}
          , {'name': 'Artist 3', 'tracks': [
                {'id': '3', 'name': 'Track 3'}]}
          , {'name': 'Artist 4', 'tracks': []}
        ]
        
        mock_track_artists = {
            '1': [{'name': 'Artist 2'}, {'name': 'Artist 1'}]
          , '2': [{'name': 'Artist 2'}, {'name': 'Artist 3'}]
          , '3': [{'name': 'Artist 3'}]
        }
        
        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: mock_track_artists.get(track_id, [])
        
        sanity_artists = self.sanityTester.sanity_artist_playlist_integrity()
        # print(sanity_artists)
        for playlist in sanity_artists:
            print(playlist)
        self.assertEqual(sanity_artists, [
            {'Playlist': 'Artist 1', 'Tracks': [{'Track': 'Track 2', 'Artists': ['Artist 2', 'Artist 3']}]}
          , {'Playlist': 'Artist 2', 'Tracks': [{'Track': 'Track 3', 'Artists': ['Artist 3']}]}
          ])
    
    def test_sanity_playable_tracks(self):
        mock_track_artists = {
            '2': [{'name': 'Artist 1'}, {'name': 'Artist 2'}]
          , '3': [{'name': 'Artist 2'}]
        }
        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: mock_track_artists.get(track_id, [])
        
        self.sanityTester.master_playlist[0] = {
            'tracks': [
                {'id': '1', 'name': 'Track 1', 'is_playable': True, 'is_local': False}
              , {'id': '2', 'name': 'Track 2', 'is_playable': False, 'is_local': False}
              , {'id': '3', 'name': 'Track 3', 'is_playable': False, 'is_local': False}
              , {'id': '4', 'name': 'Track 4', 'is_playable': False, 'is_local': True}
              , {'id': '5', 'name': 'Track 5', 'is_playable': True, 'is_local': True}
            ]}

        playable_tracks = self.sanityTester.sanity_playable_tracks()
        self.assertEqual(playable_tracks, [
            {'Track': 'Track 2', 'Artists': ['Artist 1', 'Artist 2']}
          , {'Track': 'Track 3', 'Artists': ['Artist 2']}
          ])

    def test_run_suite(self):
        self.sanityTester.run_suite()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════