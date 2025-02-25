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
        
        self.mock_spotify.create_playlist.return_value = 'test_playlist_id'
        self.mock_spotify.gather_tracks_by_artist.side_effect = lambda artist_id, start_date=None, end_date=None: {
            'artist_1': ['track_1', 'track_2'],
            'artist_2': ['track_3', 'track_4'],
            'artist_3': ['track_5', 'track_6']
        }.get(artist_id, [])
        start_date = '2025-02-24'
        end_date = '2025-02-25'
        playlist_id = self.mFeatures.generate_artist_release(['artist_1', 'artist_3']
                                                             , 'test_playlist_name', 'test_playlist_desc'
                                                             , start_date=start_date, end_date=end_date)
        # Verify playlist is created
        self.mock_spotify.create_playlist.assert_called_once_with('test_playlist_name', description='test_playlist_desc')
        # Verify every artist is called in our list to gather the tracks
        self.mock_spotify.gather_tracks_by_artist.assert_has_calls([
            mock.call('artist_1', start_date=start_date, end_date=end_date),
            mock.call('artist_3', start_date=start_date, end_date=end_date)
        ], any_order=True)
        self.assertEqual(self.mock_spotify.gather_tracks_by_artist.call_count, 2)
        # Verify the tracks are added to the playlist
        self.mock_spotify.add_tracks_to_playlist.assert_called_once_with('test_playlist_id'
                                                                         , ['track_1', 'track_2', 'track_5', 'track_6'])
        # Verify the playlist is returned
        self.assertEqual(playlist_id, 'test_playlist_id')
        
        # Test No Artists
        self.mock_spotify.create_playlist.reset_mock()
        self.mock_spotify.gather_tracks_by_artist.reset_mock()
        self.mock_spotify.add_tracks_to_playlist.reset_mock()
        self.mock_spotify.create_playlist.assert_not_called()
        self.mock_spotify.gather_tracks_by_artist.assert_not_called()
        self.mock_spotify.add_tracks_to_playlist.assert_not_called()
        self.assertIsNone(self.mFeatures.generate_artist_release([], 'test_playlist_name', 'test_playlist_desc'))
    
    @mock.patch('src.features.Misc_Features.datetime')
    def test_distribute_tracks_to_collections_from_playlist(self, MockDateTime):
        # Keep Date Consistent 
        MockDateTime.today.return_value.year = 9999
        # Things to verify
        # 1. Playlist is grabbed
        # 2. Collections are grabbed
            # 2a. If collections are missing exception is raised
        # 3. Tracks are grabbed from the playlist
        # 4. Tracks are verified for their contributing artists
        # 5. Tracks are added to the artist collection
        # 6. Tracks are added to the master and years collection

        self.mock_spotify.get_user_playlists.return_value = [
            {'id': 'artist_playlist_id_1', 'name': '__Artist One'}
            , {'id': 'artist_playlist_id_3', 'name': '__Artist Three'}
            , {'id': 'artist_playlist_id_4', 'name': '__Artist Four'}
            , {'id': Test_Settings.MASTER_MIX_ID, 'name': 'Master Mix'}
            , {'id': 'years_playlist_id', 'name': '9999'}
        ]
        
        self.mock_spotify.get_playlist_tracks.side_effect = lambda playlist_id, track_info=None, artist_info=None: {
            # No Tracks
            'playlist_id_0': []
            # Test Single Track
            , 'playlist_id_1': [{'id': 'track_1', 'name': 'Track One', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}]
            # Test Multiple Tracks
            , 'playlist_id_2': [{'id': 'track_2', 'name': 'Track Two', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}
                                , {'id': 'track_3', 'name': 'Track Three', 'artists': [{'id': 'artist_3', 'name': 'Artist Three'}]}]
            # Test Tracks From Artist We Don't Follow
            , 'playlist_id_3': [{'id': 'track_2', 'name': 'Track Two', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}
                                , {'id': 'track_3', 'name': 'Track Three', 'artists': [{'id': 'artist_2', 'name': 'Artist Two'}]}]
            # Test Duplicate Tracks
            , 'playlist_id_4': [{'id': 'track_4', 'name': 'Track Four', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}
                                , {'id': 'track_4', 'name': 'Track Four', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}
                                , {'id': 'track_5', 'name': 'Track Five', 'artists': [{'id': 'artist_3', 'name': 'Artist Three'}]}
                                , {'id': 'track_6', 'name': 'Track Six', 'artists': [{'id': 'artist_4', 'name': 'Artist Four'}]}]
            # Test Local Tracks
            , 'playlist_id_5': [{'id': 'track_7', 'name': 'Track Seven', 'artists': [{'id': None, 'name': 'Artist One'}]}
                                , {'id': 'track_8', 'name': 'Track Eight', 'artists': []}
                                , {'id': 'track_9', 'name': 'Track Nine', 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}]
            # Test MACRO_LIST Tracks
            , 'playlist_id_6': [{'id': Test_Settings.DISTRIBUTE_TRACKS_MACRO_ID, 'name': 'Macro Track'
                                 , 'artists': [{'id': 'artist_1', 'name': 'Artist One'}]}
                                , {'id': 'track_3', 'name': 'Track Three', 'artists': [{'id': 'artist_3', 'name': 'Artist Three'}]}]
        }.get(playlist_id, [])
        
        # Test Playlist With No Tracks
        self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_0')
        self.mock_spotify.get_playlist_tracks.assert_called_with('playlist_id_0', track_info=mock.ANY, artist_info=mock.ANY)
        self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
            mock.call(Test_Settings.MASTER_MIX_ID, [])
            , mock.call('years_playlist_id', [])
        ], any_order=True)
        self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 2)
        self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()
        
        # Test Playlist With Tracks
        self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_1')
        self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
            mock.call(Test_Settings.MASTER_MIX_ID, ['track_1'])
            , mock.call('years_playlist_id', ['track_1'])
            , mock.call('artist_playlist_id_1', ['track_1'])
        ], any_order=True)
        self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 3)
        self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()

        # Test Multiple
        self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_2')
        self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
            mock.call(Test_Settings.MASTER_MIX_ID, ['track_2', 'track_3'])
            , mock.call('years_playlist_id', ['track_2', 'track_3'])
            , mock.call('artist_playlist_id_1', ['track_2'])
            , mock.call('artist_playlist_id_3', ['track_3'])
        ], any_order=True)
        self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 4)
        self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()
        
        # Test Playlist With Tracks From Artists We Do Not Follow
        with mock.patch.object(self.mFeatures, 'logger') as mock_logger:
            self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_3')
            self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
                mock.call(Test_Settings.MASTER_MIX_ID, ['track_2'])
                , mock.call('years_playlist_id', ['track_2'])
                , mock.call('artist_playlist_id_1', ['track_2'])
            ], any_order=True)
            self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 3)
            self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()
            mock_logger.error.assert_called_once_with("NO CONTRIBUTING ARTIST FOUND")
            mock_logger.reset_mock()
        
        # Test Playlist With Duplicate Tracks
            self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_4')
            self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
                mock.call(Test_Settings.MASTER_MIX_ID, ['track_4', 'track_4', 'track_5', 'track_6'])
                , mock.call('years_playlist_id', ['track_4', 'track_4', 'track_5', 'track_6'])
                , mock.call('artist_playlist_id_1', ['track_4', 'track_4'])
                , mock.call('artist_playlist_id_3', ['track_5'])
                , mock.call('artist_playlist_id_4', ['track_6'])
            ], any_order=True)
            self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 5)
            self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()
            mock_logger.error.assert_not_called()
        
        # Test Playlist With Local Tracks
        self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_5')
        self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
            mock.call(Test_Settings.MASTER_MIX_ID, ['track_9'])
            , mock.call('years_playlist_id', ['track_9'])
            , mock.call('artist_playlist_id_1', ['track_9'])
        ], any_order=True)
        self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 3)
        self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()
        
        # Test Playlist With Tracks and MACRO_LIST Tracks
        self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_6')
        self.mock_spotify.add_unique_tracks_to_playlist.assert_has_calls([
            mock.call(Test_Settings.MASTER_MIX_ID, ['track_3'])
            , mock.call('years_playlist_id', ['track_3'])
            , mock.call('artist_playlist_id_3', ['track_3'])
        ], any_order=True)
        self.assertEqual(self.mock_spotify.add_unique_tracks_to_playlist.call_count, 3)
        self.mock_spotify.add_unique_tracks_to_playlist.reset_mock()

        # Missing Years
        self.mock_spotify.get_user_playlists.return_value = [
            {'id': 'artist_playlist_id_1', 'name': '__Artist One'}
            , {'id': Test_Settings.MASTER_MIX_ID, 'name': 'Master Mix'}
        ]
        with self.assertRaises(Exception):
            self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_0')
        # Missing Master
        self.mock_spotify.get_user_playlists.return_value = [
            {'id': 'artist_playlist_id_1', 'name': '__Artist One'}
            , {'id': 'years_playlist_id', 'name': '9999'}
        ]
        with self.assertRaises(Exception):
            self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_0')
        # Missing Artists
        self.mock_spotify.get_user_playlists.return_value = [
            {'id': Test_Settings.MASTER_MIX_ID, 'name': 'Master Mix'}
            , {'id': 'years_playlist_id', 'name': '9999'}
        ]
        with self.assertRaises(Exception):
            self.mFeatures.distribute_tracks_to_collections_from_playlist('playlist_id_0')
    
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