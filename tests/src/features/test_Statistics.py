# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - STATISTICS                  CREATED: 2025-03-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Statistics.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import unittest
from unittest import mock

from tests.helpers.mocked_Settings import Test_Settings
from src.features.Statistics       import SpotifyStatistics

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Misc Features functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestStatistics(unittest.TestCase):
    
    @mock.patch('src.features.Statistics.DatabaseHelpers')
    def setUp(self, MockDBH):
        self.statistics = SpotifyStatistics()
        self.mock_dbh = mock.MagicMock()
        self.statistics.dbh = self.mock_dbh

    @mock.patch('src.features.Statistics.Settings', Test_Settings)
    def test_generate_featured_artists_list(self):

        Test_Settings.PLAYLIST_IDS_NOT_IN_ARTISTS = ['playlist_id_1', 'playlist_id_2']
        self.mock_dbh.db_get_user_followed_artists.return_value = [{'id': 'artist_1'}, {'id': 'artist_2'}]
        
        self.mock_dbh.db_get_tracks_from_playlist.side_effect = lambda playlist_id: {
            Test_Settings.MASTER_MIX_ID: [{'id': 'track_1', 'name': 'Track One', 'is_local': False}
                                          , {'id': 'track_2', 'name': 'Track Two', 'is_local': False}
                                          , {'id': 'track_3', 'name': 'Track Three', 'is_local': False}
                                          , {'id': 'track_4', 'name': 'Track Four', 'is_local': False}
                                          , {'id': 'track_5', 'name': 'Track Five', 'is_local': False}
                                          , {'id': 'track_6', 'name': 'Track Six', 'is_local': False}
                                          , {'id': 'track_7', 'name': 'Track Seven', 'is_local': True}]
            , 'playlist_id_1': [{'id': 'track_3'}]
        }.get(playlist_id, [])
        
        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: {
            'track_1': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_2', 'name': 'Artist Two'}]
            , 'track_2': [{'id': 'artist_1', 'name': 'Artist One'}]
            , 'track_3': [{'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_4': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_5': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_4', 'name': 'Artist Four'}]
            , 'track_6': [{'id': 'artist_2', 'name': 'Artist Two'}, {'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_7': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_3', 'name': 'Artist Three'}]
        }.get(track_id, [])

        print(self.statistics.generate_featured_artists_list(2))

        self.assertEqual(self.statistics.generate_featured_artists_list(2)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 2
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six']}
                          , {'Artist Name': 'Artist Four', 'Number of Tracks': 1
                             , 'Unique Artists': ['Artist One']
                             , 'Track Names': ['Track Five']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(1)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 2
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(0), [])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
