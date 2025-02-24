# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SHUFFLE STYLES              CREATED: 2025-02-24          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Shuffle_Styles.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import unittest
from unittest import mock

from tests.helpers.mocked_Settings import Test_Settings
from src.features.Misc_Features    import MiscFeatures

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Shuffle Styles functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Misc_Features.Settings', Test_Settings)
class TestMiscFeatures(unittest.TestCase):
    
    def setUp(self):
        self.mock_spotify = mock.MagicMock()
        self.mFeatures = MiscFeatures(self.mock_spotify)

    def test_init(self):
        self.assertEqual(self.mFeatures.spotify, self.mock_spotify)
        self.assertEqual(self.mFeatures.logger, logging.getLogger())
        
        logger = mock.MagicMock()
        mFeaturesLog = MiscFeatures(self.mock_spotify, logger=logger)
        self.assertEqual(mFeaturesLog.logger, logger)
        
    def test_get_first_artist_from_playlist(self):
        # Test Single Track / Single Artist
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_1'
                                                               , 'artists': [{'id': 'test_id'}]}]
        self.assertEqual(self.mFeatures.get_first_artist_from_playlist('test_playlist'), 'test_id')
        
        # Test Single Track / Multiple Artists
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_1'
                                                               , 'artists': [{'id': 'test_id_2'}
                                                                             , {'id': 'test_id'}]}]
        self.assertEqual(self.mFeatures.get_first_artist_from_playlist('test_playlist'), 'test_id_2')
        
        # Test Multiple Tracks / Single Artist
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_2'
                                                               , 'artists': [{'id': 'test_id_1'}]}
                                                              , {'id': 'track_id_3'
                                                               , 'artists': [{'id': 'test_id_4'}]}
                                                              ,{'id': 'track_id_4'
                                                               , 'artists': [{'id': 'test_id_5'}]}]
        self.assertEqual(self.mFeatures.get_first_artist_from_playlist('test_playlist'), 'test_id_1')
        
        # Test Multiple Tracks / Multiple Artists
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_3'
                                                               , 'artists': [{'id': 'test_id_10'}
                                                                             , {'id': 'test_id_1'}]}
                                                              , {'id': 'track_id_3'
                                                               , 'artists': [{'id': 'test_id_43'}
                                                                            , {'id': 'test_id_1'}]}
                                                              ,{'id': 'track_id_4'
                                                               , 'artists': [{'id': 'test_id_51'}
                                                                            , {'id': 'test_id_1'}]}]
        self.assertEqual(self.mFeatures.get_first_artist_from_playlist('test_playlist'), 'test_id_10')
        
        # Test No Tracks
        self.mock_spotify.get_playlist_tracks.return_value = []
        self.assertIsNone(self.mFeatures.get_first_artist_from_playlist('test_playlist'))
        
        # Test No Artist Key
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_3'}]
        self.assertIsNone(self.mFeatures.get_first_artist_from_playlist('test_playlist'))
        
        # Test No Artists
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': 'track_id_3', 'artists': []}]
        self.assertIsNone(self.mFeatures.get_first_artist_from_playlist('test_playlist'))
        
        # Test Only MACRO_LIST Track
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': Test_Settings.GEN_ARTIST_MACRO_ID
                                                               , 'artists': [{'id' : 'test_id_1'}]}]
        self.assertIsNone(self.mFeatures.get_first_artist_from_playlist('test_playlist'))
        
        # Test MACRO_LIST Track and Regular Track
        self.mock_spotify.get_playlist_tracks.return_value = [{'id': Test_Settings.GEN_ARTIST_MACRO_ID
                                                               , 'artists': [{'id' : 'test_id_1'}]}
                                                              ,{'id': 'track_id_4'
                                                               , 'artists': [{'id': 'test_id_51'}
                                                                            , {'id': 'test_id_1'}]}]
        self.assertEqual(self.mFeatures.get_first_artist_from_playlist('test_playlist'), 'test_id_51')
    
    def test_generate_artist_release(self):
        # generate_artist_release
        pass
    
    def test_distribute_tracks_to_collections_from_playlist(self):
        # distribute_tracks_to_collections_from_playlist
        pass
    
    def test_reorganize_playlist(self):
        # reorganize_playlist
        pass
    
    def test_update_daily_latest_playlist(self):
        # update_daily_latest_playlist
        pass
    
    def test_generate_featured_artists_list(self):
        # generate_featured_artists_list
        pass


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════