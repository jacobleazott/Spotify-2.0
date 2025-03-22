# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - GSH                         CREATED: 2024-09-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'General_Spotify_Helpers.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import inspect
import unittest

from datetime import datetime
from unittest import mock

import src.General_Spotify_Helpers  as gsh
import tests.helpers.tester_helpers as thelp

from src.helpers.Settings           import Settings
from tests.helpers.mocked_Settings  import Test_Settings
from tests.helpers.mocked_spotipy   import MockedSpotipyProxy

from pprint import pprint

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all GSH functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.General_Spotify_Helpers.SpotipyProxy', new=MockedSpotipyProxy)
class TestGSH(unittest.TestCase):
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # NON CLASS FUNCTIONS ═════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    def test_validate_inputs(self):
        with self.assertRaises(Exception): gsh.validate_inputs([1, "1"], [int])
        with self.assertRaises(Exception): gsh.validate_inputs([1], [int, dict])
        with self.assertRaises(Exception): gsh.validate_inputs([1], [str])
        with self.assertRaises(Exception): gsh.validate_inputs([1], [])
        with self.assertRaises(Exception): gsh.validate_inputs([], [dict])
        with self.assertRaises(Exception): gsh.validate_inputs([], [1])
        with self.assertRaises(Exception): gsh.validate_inputs([int], [1])
        
        gsh.validate_inputs(["test", 10], [str, int])
        gsh.validate_inputs([], [])
    
    def test_chunks(self):
        with self.assertRaises(Exception): gsh.chunks(None, 10)
        with self.assertRaises(Exception): gsh.chunks(['1'], "10")
        with self.assertRaises(Exception): gsh.chunks(1, 1)
        
        test_list_1 = ['1', '2', '3', '4', '5', '6']
        self.assertEqual(gsh.chunks(test_list_1, 0),   [['1'], ['2'], ['3'], ['4'], ['5'], ['6']])
        self.assertEqual(gsh.chunks(test_list_1, -10), [['1'], ['2'], ['3'], ['4'], ['5'], ['6']])
        self.assertEqual(gsh.chunks(test_list_1, 1),   [['1'], ['2'], ['3'], ['4'], ['5'], ['6']])
        self.assertEqual(gsh.chunks(test_list_1, 2),   [['1', '2'], ['3', '4'], ['5', '6']])
        self.assertEqual(gsh.chunks(test_list_1, 3),   [['1', '2', '3'], ['4', '5', '6']])
        self.assertEqual(gsh.chunks(test_list_1, 4),   [['1', '2', '3', '4'], ['5', '6']])
        self.assertEqual(gsh.chunks(test_list_1, 5),   [['1', '2', '3', '4', '5'], ['6']])
        self.assertEqual(gsh.chunks(test_list_1, 6),   [['1', '2', '3', '4', '5', '6']])
        self.assertEqual(gsh.chunks(test_list_1, 7),   [['1', '2', '3', '4', '5', '6']])
        self.assertEqual(gsh.chunks(test_list_1, 20),  [['1', '2', '3', '4', '5', '6']])
        
        self.assertEqual(gsh.chunks([], 0),   [])
        self.assertEqual(gsh.chunks([], 5),   [])
    
    def test_get_generic_field(self):
        with self.assertRaises(Exception): gsh.get_generic_field("data", ["id", "name"])
        with self.assertRaises(Exception): gsh.get_generic_field(None, ["id"])
        with self.assertRaises(Exception): gsh.get_generic_field({"test": 1}, None)
        with self.assertRaises(KeyError):  gsh.get_generic_field({"test": 1}, ["id"])
        
        self.assertEqual(gsh.get_generic_field({"test": 1}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "test"]), ["weak", 1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "id"]), ["weak", "weak"])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, []), [])
        self.assertEqual(gsh.get_generic_field({"test": {}, "id": []}, ["test", "id"]), [{}, []])
        self.assertEqual(gsh.get_generic_field({"test": {"world": 2}, "id": ["val1", "val2"]}, 
                                               ["test", "id"]), [{"world": 2}, ["val1", "val2"]])
        self.assertEqual(gsh.get_generic_field({}, []), [])
   
    def test_get_elements_in_date_range(self):
        print("")
        
        with self.assertRaises(Exception): gsh.get_elements_in_date_range([""], datetime(0, 0, 0), "i")
        with self.assertRaises(Exception): gsh.get_elements_in_date_range([""], 2, datetime(0, 0, 0))
        with self.assertRaises(Exception): gsh.get_elements_in_date_range(1, datetime(0, 0, 0), datetime(0, 0, 0))
        
        def tester(start_date, end_date, key):
            results = gsh.get_elements_in_date_range(release_date_test, start_date, end_date)
            calc_results = [val for idx, val in enumerate(release_date_test) if key[idx]]
            
            for res in results:
                if res not in calc_results:
                    print(f"FAILED [Additional Value]: {res}")
                    assert False

            for calc_res in calc_results:
                if calc_res not in results:
                    print(f"FAILED [Missing Value]   : {calc_res}")
                    assert False
                    
        release_date_test =  [  {'release_date': '1998'},
                                {'release_date': '1998-05'},
                                {'release_date': '1998-06-02'},
                                {'release_date': '2001'},
                                {'release_date': '2001-01'},
                                {'release_date': '2001-01-05'},
                                {'release_date': '1999'},
                                {'release_date': '1999-05'},
                                {'release_date': '1999-07-16'},
                                {'release_date': '2000'},
                                {'release_date': '2000-1'},
                                {'release_date': '2000-3'},
                                {'release_date': '2000-4'},
                                {'release_date': '2000-12'},
                                {'release_date': '2000-01-15'},
                                {'release_date': '2000-01-16'},
                                {'release_date': '2000-01-17'},
                                {'release_date': '2000-01-25'},
                                {'release_date': '2000-01-26'},
                                {'release_date': '2000-01-27'},
                                {'release_date': '2000-03-05'},
                                {'release_date': '2000-04-10'},
                                {'release_date': '2000-12-30'},
                                {'release_date': '2000-12-31'},
                                {'release_date': 's'},
                                {'release_date': ''}]
        # Y-M-D, Y-M, Y, []
        # Y-M-D only counts if given day is in range
        # Y-M only counts if last day of the month is included
        # Y only counts if last day of year is included (12/31)
             
        print(f"\t{inspect.stack()[0][3]}: Inter Month (End Month) -----------------------------")
        #   2000-12-10 -> 2000-12-31    Should include 2000-12-10 -> 2000-12-31, 2000-12, 2000
        tester(datetime(2000, 12, 10),  datetime(2000, 12, 31), [False, False, False, False, False, 
                                                                 False, False, False, False, True ,                                                   False, False, False, True , False, 
                                                                 False, False, False, False, False, 
                                                                 False, False, True , True , True , 
                                                                 True])
        print(f"\t{inspect.stack()[0][3]}: Inter Month -----------------------------------------")
        #   2000-01-16 -> 2000-01-26    Should include 2000-01-16 -> 2000-01-26
        tester(datetime(2000, 1, 16),   datetime(2000, 1, 26),  [False, False, False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 True , True , True , True , False, 
                                                                 False, False, False, False, True , 
                                                                 True])

        print(f"\t{inspect.stack()[0][3]}: Full Month ------------------------------------------")
        #   2000-03-01 -> 2000-03-31    Should include 2000-03-01 -> 2000-03-31, 2000-03
        tester(datetime(2000, 3, 1),    datetime(2000, 3, 31),  [False, False, False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 False, True , False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 True , False, False, False, True , 
                                                                 True])

        print(f"\t{inspect.stack()[0][3]}: 2 Full Months ---------------------------------------")
        #   2000-03-01 -> 2000-04-30    Should include 2000-03-01 -> 2000-04-30, 2000-03, 2000-04
        tester(datetime(2000, 3, 1),    datetime(2000, 4, 30),  [False, False, False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 False, True , True , False, False, 
                                                                 False, False, False, False, False, 
                                                                 True , True , False, False, True , 
                                                                 True])

        print(f"\t{inspect.stack()[0][3]}: 2 Partial Months ------------------------------------")
        # 2000-03-05 -> 2000-04-25    Should include 2000-03-05 -> 2000-04-25, 2000-03
        tester(datetime(2000, 3, 5),    datetime(2000, 4, 25),  [False, False, False, False, False, 
                                                                 False, False, False, False, False, 
                                                                 False, True , False, False, False,
                                                                 False, False, False, False, False, 
                                                                 True , True , False, False, True , 
                                                                 True])

        print(f"\t{inspect.stack()[0][3]}: Full Year -------------------------------------------")
        #   2000-01-01 -> 2000-12-31    Should include 2000-01-01 -> 2000-12-31, 2000-01 -> 2000-12, 2000
        tester(datetime(2000, 1, 1),    datetime(2000, 12, 31), [False, False, False, False, False, 
                                                                 False, False, False, False, True , 
                                                                 True , True , True , True , True , 
                                                                 True , True , True , True , True , 
                                                                 True , True , True , True , True , 
                                                                 True])

        print(f"\t{inspect.stack()[0][3]}: Multi Year ------------------------------------------")
        #   1999-11-02 -> 2000-04-25    Should include 1999-11-02 -> 2000-04-25, 1999-11 -> 2000-03, 1999
        tester(datetime(1999, 11, 2),   datetime(2000, 4, 25),  [False, False, False, False, False, 
                                                                 False, True , False, False, False, 
                                                                 True , True , False, False, True , 
                                                                 True , True , True , True , True , 
                                                                 True , True , False, False, True , 
                                                                 True])
    
    def test_scopes(self):
        class MockSpotifyClass:
            def __init__(cls):
                cls.spotify = mock.MagicMock()
                cls.spotify._scopes = []

            @gsh.scopes(["playlist-read-private", "user-library-read"])
            def fetch_data(cls):
                self.assertEqual(cls.spotify._scopes, ["playlist-read-private", "user-library-read"])
                return "Data"
        
        client = MockSpotifyClass()
        self.assertEqual(client.spotify._scopes, [])
        self.assertEqual(client.fetch_data(), "Data")
        self.assertEqual(client.spotify._scopes, [])
    
    def test_build_field_structure(self):
        # No info provided
        self.assertEqual(gsh.build_field_structure(), {})
        # 'info' provided
        self.assertEqual(gsh.build_field_structure(info=['name', 'id'])
                         , {'name': True, 'id': True})
        # 'track_info' provided
        self.assertEqual(gsh.build_field_structure(track_info=['name', 'id'])
                         , {'track': {'name': True, 'id': True}})
        # 'album_info' provided
        self.assertEqual(gsh.build_field_structure(album_info=['name', 'id'])
                         , {'track': {'album': {'name': True, 'id': True}}})
        # 'artist_info' provided
        self.assertEqual(gsh.build_field_structure(artist_info=['name', 'id'])
                         , {'track': {'artists': {'name': True, 'id': True}}})
        # all info given
        self.assertEqual(gsh.build_field_structure(info=['name', 'id'], track_info=['name', 'id']
                                                   , album_info=['name', 'id'], artist_info=['name', 'id'])
                         , {'name': True, 'id': True, 'track': {'name': True, 'id': True
                                                                , 'album': {'name': True, 'id': True}
                                                                , 'artists': {'name': True, 'id': True}}})
    
    def test_find_main_iterator(self):
        # Path not found
        self.assertEqual(gsh.find_main_iterator({}), ({}, None))
        self.assertEqual(gsh.find_main_iterator({"no_item": 10}), ({"no_item": 10}, None))
        
        # Path with items
        response = {"not_valid": 1, "items": [{"id": "Track1"}]}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([{"id": "Track1"}], ["items"]))
        
        # Path with item
        response = {"item": {"name": "Single Track"}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ({"name": "Single Track"}, ["item"]))
        
        # Path with playlists -> items
        response = {"playlists": {"items": [{"name": "Playlist 1"}]}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([{'name': 'Playlist 1'}], ['playlists', 'items']))
        
        # path with albums -> items and empty list
        response = {"albums": {"items": []}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([], ["albums", "items"]))
        
        # Path with tracks -> items
        response = {"tracks": {"items": []}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([], ["tracks", "items"]))
        
        # Path with artists -> items
        response = {"artists": {"items": []}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([], ["artists", "items"]))
        
        # Path with albums
        response = {"albums": {"Test": "Value"}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ({"Test": "Value"}, ["albums"]))
        
        # Path with artists
        response = {"artists": [{"Test": "Value"}]}
        self.assertEqual(gsh.find_main_iterator(response)
                         , ([{"Test": "Value"}], ["artists"]))
        
        # Invalid path in a dictionary structure
        response = {"tracks": {}}
        self.assertEqual(gsh.find_main_iterator(response)
                         , (response, None))

    def test_extract_fields(self):
        # Test List
        data = [{"name": "Track1", "duration": 30}, {"name": "Track2", "duration": 25}]
        field_structure = {'name': True}
        self.assertEqual(gsh.extract_fields(data, field_structure), [{"name": "Track1"}, {"name": "Track2"}])
        
        # Test Dictionary
        data = {"name": "Track1", "duration": 30}
        field_structure = {'name': True, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), data)
        
        # Test List of Dictionaries
        data = [{"name": "Track1", "duration": 30}, {"name": "Track2", "duration": 25}]
        field_structure = {'name': True, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), data)
        
        # Test Dictionary of Lists
        data = {"name": ["Track1", "Track2"], "duration": [30, 25]}
        field_structure = {'name': True, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), data)
        
        # Test Non List/ Dictionary
        data = "Test"
        field_structure = {'name': True, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), data)
        
        # Test Sub Dictionary
        data = {"name": "Track1", "album": {"release": 30, "name": "Album1"}}
        field_structure = {'name': True, "album": {"name": True}}
        self.assertEqual(gsh.extract_fields(data, field_structure), {"name": "Track1", "album": {"name": "Album1"}})
        
        # Test Empty 'field_structure'
        data = {"name": "Track1", "duration": 30}
        field_structure = {}
        self.assertEqual(gsh.extract_fields(data, field_structure), {})
        
        # Test Missing 'info' from 'field_structure'
        data = [{"name": "Track1", "duration": 30}, {"name": "Track2"}]
        field_structure = {'duration': True}
        self.assertEqual(gsh.extract_fields(data, field_structure), [{"duration": 30}, {"duration": None}])
        
        # Test False in 'field_structure'
        data = {'name': "Track1", "duration": 30}
        field_structure = {'name': False, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), {'duration': 30})
        
        # Test Empty List
        data = []
        field_structure = {'name': True, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), [])
        
        # Test Empty Dict
        data = {}
        field_structure = {'name': False, "duration": True}
        self.assertEqual(gsh.extract_fields(data, field_structure), {'duration': None})
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # "PRIVATE" CLASS FUNCTIONS ═══════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def test_gather_data(self):
        # Test Extend On List
        
        # Test Extend On Dictionary
        
        # Test Base Level Next
        
        # Test Nested Next
        
        # Test No Next
        
        pass

    def test_validate_scope(self):
        test_scopes = [ "user-read-private"
                        , "playlist-modify-public"
                        , "playlist-modify-private"
                        , "user-library-read"]
        
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes=test_scopes

        with self.assertRaises(Exception): spotify._validate_scope()
        with self.assertRaises(Exception): spotify._validate_scope("user-read-private")
        with self.assertRaises(Exception): spotify._validate_scope(["invalid-scope"])
        with self.assertRaises(Exception): spotify._validate_scope(
            ["user-read-private", "invalid-scope", "playlist-modify-private"])
        
        spotify._validate_scope([])
        spotify._validate_scope(["user-read-private", "playlist-modify-public"])
        spotify._validate_scope(["user-library-read"])
        spotify._validate_scope(
            ["user-read-private", "playlist-modify-public", "playlist-modify-private", "user-library-read"])
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # CLASS FUNCTIONS ═════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    def test_get_user_artists(self):
        # Currently don't have any way to add or remove followed artists since I never want the project to do this.
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        self.assertEqual(spotify.get_user_artists(), [{'id': 'Ar002'}, {'id': 'Ar003'}, {'id': 'Ar004'}])
        self.assertEqual(spotify.get_user_artists(info=['id', 'name']), [{'id': 'Ar002', 'name': 'Fake Artist 2'},
                                                                         {'id': 'Ar003', 'name': 'Fake Artist 3'},
                                                                         {'id': 'Ar004', 'name': 'Fake Artist 4'}])

    def test_get_user_playlists(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        self.assertEqual(spotify.get_user_playlists(), 
                         [{'id': 'Pl001'}, {'id': 'Pl002'}, {'id': 'Pl003'}, {'id': 'Pl004'}])
        self.assertEqual(spotify.get_user_playlists(info=['name', 'id']), [{'id': 'Pl001', 'name': 'Fake Playlist 1'},
                                                                           {'id': 'Pl002', 'name': 'Fake Playlist 2'},
                                                                           {'id': 'Pl003', 'name': 'Fake Playlist 3'},
                                                                           {'id': 'Pl004', 'name': 'Fake Playlist 4'}])
        
        spotify.create_playlist("Tested Playlist")
        self.assertEqual(spotify.get_user_playlists(info=['name', 'id']), [{'id': 'Pl001', 'name': 'Fake Playlist 1'},
                                                                           {'id': 'Pl002', 'name': 'Fake Playlist 2'},
                                                                           {'id': 'Pl003', 'name': 'Fake Playlist 3'},
                                                                           {'id': 'Pl004', 'name': 'Fake Playlist 4'},
                                                                           {'id': 'Pl005', 'name': 'Tested Playlist'}])
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYBACK ════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    def test_get_playback_state(self):
        # A lot of this functionality is also tested under the 'test_change_playback()'
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        
        # Test "Normal" Return
        self.assertEqual(spotify.get_playback_state(), {
            'context': {'id': 'Pl001', 'type': 'playlist'},
            'currently_playing_type': 'track',
            'is_playing': True,
            'repeat_state': 'off',
            'shuffle_state': False,
            'track': {'artists': [{'id': 'Ar000'}], 'id': 'Tr000'}})
        
        # Test None Context
        spotify.sp.current_playback_response['context'] = None
        self.assertEqual(spotify.get_playback_state(), {
            'context': None,
            'currently_playing_type': 'track',
            'is_playing': True,
            'repeat_state': 'off',
            'shuffle_state': False,
            'track': {'artists': [{'id': 'Ar000'}], 'id': 'Tr000'}})
        
        # Test Different Track Info
        self.assertEqual(spotify.get_playback_state(track_info=['name', 'duration_ms'])['track'], {
            'artists': [{'id': 'Ar000'}], 
            'name': 'Fake Track 0', 
            'duration_ms': 0})
        
        # Test Different Artist Info
        self.assertEqual(spotify.get_playback_state(track_info=['name'], artist_info=['name'])['track'], {
            'artists': [{'name': 'Fake Artist 0'}], 
            'name': 'Fake Track 0', })
        
        # Test None 'Item'
        spotify.sp.current_playback_response['item'] = None
        self.assertEqual(spotify.get_playback_state(), None)

    @mock.patch("time.sleep", return_value=None)
    def test_write_to_queue(self, mock_sleep):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        # Verify Queue Is Empty Before Testing
        self.assertEqual(spotify.sp.user_queue, [])
        # Adding Empty Track Id List
        spotify.write_to_queue([])
        self.assertEqual(spotify.sp.user_queue, [])
        # Adding One Track
        spotify.write_to_queue(["Tr001"])
        self.assertEqual(spotify.sp.user_queue, ["Tr001"])
        # Adding Multiple Tracks With Duplicate
        spotify.write_to_queue(["Tr001", "Tr010"])
        self.assertEqual(spotify.sp.user_queue, ["Tr001", "Tr001", "Tr010"])

    def test_change_playback(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        # No Changes
        spotify.change_playback()
        # Verify default values
        playback = spotify.get_playback_state()
        pprint(playback)
        self.assertEqual([playback['track']['id'], playback['shuffle_state']
                          , playback['context']['id'], playback['is_playing']]
                         , ['Tr000', False, 'Pl001', True])
        # Pause Playback
        spotify.change_playback(pause=True)
        playback = spotify.get_playback_state()
        self.assertEqual([playback['track']['id'], playback['shuffle_state']
                          , playback['context']['id'], playback['is_playing']]
                         , ['Tr000', False, 'Pl001', False])
        # Add Tracks To Internal Queue and SKip
        spotify.sp.user_queue += [spotify.sp.track('Tr001'), spotify.sp.track('Tr009'), spotify.sp.track('Tr005')]
        spotify.change_playback(skip="next")
        playback = spotify.get_playback_state()
        self.assertEqual([playback['track']['id'], playback['shuffle_state']
                          , playback['context']['id'], playback['is_playing']]
                         , ['Tr001', False, 'Pl001', True])
        # Verify Skip
        spotify.change_playback(skip="next")
        playback = spotify.get_playback_state()
        self.assertEqual([playback['track']['id'], playback['shuffle_state']
                          , playback['context']['id'], playback['is_playing']]
                         , ['Tr009', False, 'Pl001', True])
        # Verify Prev
        spotify.change_playback(skip="prev")
        playback = spotify.get_playback_state()
        self.assertEqual([playback['track']['id'], playback['shuffle_state'], playback['context']['id']
                          , playback['is_playing'], playback['repeat_state']]
                         , ['Tr001', False, 'Pl001', True, 'off'])
        # Multiple changes
        spotify.change_playback(skip="next", shuffle=True, repeat='track')
        playback = spotify.get_playback_state()
        self.assertEqual([playback['track']['id'], playback['shuffle_state'], playback['context']['id']
                          , playback['is_playing'], playback['repeat_state']]
                         , ['Tr005', True, 'Pl001', True, 'track'])

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYLISTS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    def test_add_tracks_to_playlist(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        # Verify Playlist Is Empty
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("InvalidPlaylist", ["Tr001"])
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("Pl001", ["InvalidTrack"])
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("Pl001", "NonList Track")
        
        # Adding No Tracks
        spotify.add_tracks_to_playlist("Pl001", [])
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        # Added A Few Tracks
        spotify.add_tracks_to_playlist("Pl001", ["Tr001", "Tr002", "Tr004"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004"])
        # Adding Duplicate Tracks
        spotify.add_tracks_to_playlist("Pl001", ["Tr001", "Tr002", "Tr004"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004", "Tr001", "Tr002", "Tr004"])

    def test_add_unique_tracks_to_playlist(self):
        # Same test as 'test_add_tracks_to_playlist()' except that duplicates shouldn't be added.
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        # Verify Playlist Is Empty
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("InvalidPlaylist", ["Tr001"])
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("Pl001", ["InvalidTrack"])
        with self.assertRaises(Exception): spotify.add_tracks_to_playlist("Pl001", "NonList Track")
        
        # Adding No Tracks
        spotify.add_unique_tracks_to_playlist("Pl001", [])
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        # Added A Few Tracks
        spotify.add_unique_tracks_to_playlist("Pl001", ["Tr001", "Tr002", "Tr004"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004"])
        # Adding Duplicate Tracks Already In Playlist
        spotify.add_unique_tracks_to_playlist("Pl001", ["Tr001", "Tr002", "Tr004"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004"])
        # Adding Duplicate Tracks Not Already In Playlist
        spotify.add_unique_tracks_to_playlist("Pl001", ["Tr005", "Tr005", "Tr006"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004", "Tr005", "Tr006"])

    def test_get_playlist_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        # Empty Playlist
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        # "Regular" Playlist Default Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002"), 
                         [{'album': {'id': 'Al002'}, 'artists': [{'id': 'Ar002'}], 'id': 'Tr002'},
                          {'album': {'id': 'Al003'}, 'artists': [{'id': 'Ar002'}], 'id': 'Tr003'},
                          {'album': {'id': 'Al004'}, 'artists': [{'id': 'Ar002'}], 'id': 'Tr004'}])
        # No Track Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[]), 
                         [{'album': {'id': 'Al002'}, 'artists': [{'id': 'Ar002'}]},
                          {'album': {'id': 'Al003'}, 'artists': [{'id': 'Ar002'}]},
                          {'album': {'id': 'Al004'}, 'artists': [{'id': 'Ar002'}]}])
        # No Track or Artist Info
        
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[], artist_info=[]), 
                         [{'album': {'id': 'Al002'}},
                          {'album': {'id': 'Al003'}},
                          {'album': {'id': 'Al004'}}])
        # No Track, Artist, or Album Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[], artist_info=[], album_info=[]), [])
        # Different Info From Default
        self.assertEqual(
            spotify.get_playlist_tracks("Pl002", track_info=['name'], artist_info=['name'], album_info=['name']),
            [
                {'album': {'name': 'Fake Album 2'}, 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 2'}
              , {'album': {'name': 'Fake Album 3'}, 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 3'}
              , {'album': {'name': 'Fake Album 4'}, 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 4'}])
        # Duplicate Tracks and Local Tracks Default Info
        self.assertEqual(
            spotify.get_playlist_tracks("Pl004"),
            [
                {'album': {'id': None}, 'artists': [{'id': None}], 'id': None}
              , {'album': {'id': None}, 'artists': [{'id': None}], 'id': None}
              , {'album': {'id': 'Al002'}, 'artists': [{'id': 'Ar002'}], 'id': 'Tr001'}
              , {'album': {'id': 'Al002'}, 'artists': [{'id': 'Ar002'}], 'id': 'Tr001'}])
        # Duplicate Tracks and Local Tracks Extra Info
        self.assertEqual(
            spotify.get_playlist_tracks("Pl004", track_info=['id', 'name']
                                        , artist_info=['id', 'name']
                                        , album_info=['id', 'name']),
            [
                {'album': {'id': None, 'name': 'Fake Local Album 1'}
               , 'artists': [{'id': None, 'name': 'Fake Local Artist 1'}]
               , 'id': None, 'name': 'Fake Local Track 1'}

              , {'album': {'id': None, 'name': 'Fake Local Album 1'}
               , 'artists': [{'id': None, 'name': 'Fake Local Artist 1'}]
               , 'id': None, 'name': 'Fake Local Track 1'}

              , {'album': {'id': 'Al002', 'name': 'Fake Album 2'}
               , 'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}]
               , 'id': 'Tr001', 'name': 'Fake Track 1'}

              , {'album': {'id': 'Al002', 'name': 'Fake Album 2'}
               , 'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}]
               , 'id': 'Tr001', 'name': 'Fake Track 1'}])

    def test_create_playlist(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        
        empty_id = spotify.create_playlist("")
        self.assertEqual(spotify.get_playlist_data(empty_id, info=['name', 'description']), ["", ""])
        
        empty_desc_id = spotify.create_playlist("", description="")
        self.assertEqual(spotify.get_playlist_data(empty_desc_id, info=['name', 'description', 'public']), 
                         ["", "", False])
        
        public_true_id = spotify.create_playlist("Test", public=True)
        self.assertEqual(spotify.get_playlist_data(public_true_id, info=['name', 'public']), ["Test", True])

        for count in range(len(spotify.sp.playlists), 410):
            if count < 400:
                self.assertEqual(spotify.create_playlist("Test Playlist", description="tmp"), f"Pl{count+1:03d}")
            else:
                with self.assertRaises(Exception): spotify.create_playlist("Test Over Count", description="tmp tmp")
                self.assertEqual(len(spotify.sp.playlists), 400)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ARTISTS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test_change_playlist_details(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        
        empty_id = spotify.create_playlist("")
        spotify.change_playlist_details(empty_id)
        self.assertEqual(spotify.get_playlist_data(empty_id, info=['name', 'description']), ["", ""])
        
        spotify.change_playlist_details(empty_id, name="Tester")
        self.assertEqual(spotify.get_playlist_data(empty_id, info=['name', 'description']), ["Tester", ""])
        
        playlist_id = spotify.create_playlist("Default", description="set")
        spotify.change_playlist_details(playlist_id, description="Test2")
        self.assertEqual(spotify.get_playlist_data(playlist_id, info=['name', 'description']), ["Default", "Test2"])
        
        playlist_id = spotify.create_playlist("Default", description="set")
        spotify.change_playlist_details(playlist_id, name="Test1", description="Test2")
        self.assertEqual(spotify.get_playlist_data(playlist_id, info=['name', 'description']), ["Test1", "Test2"])

    @mock.patch('src.General_Spotify_Helpers.Settings', Test_Settings)
    def test_remove_all_playlist_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        Test_Settings.PLAYLISTS_WE_CAN_DELETE_FROM = ["Pl100"]
        spotify.sp.playlists.append(thelp.create_playlist("Pl100", "Fake Delete PLaylist", "no description", []))
        spotify.add_tracks_to_playlist("Pl100", ["Tr001", "Tr002", "Tr004"])
        
        with self.assertRaises(Exception): spotify.remove_all_playlist_tracks("Pl100")

        spotify._scopes.append(Test_Settings.DELETE_SCOPE)
        
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002")
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002", max_playlist_length=5)
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl100")
        self.assertEqual(len(spotify.sp.playlist_items("Pl100")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl100", max_playlist_length=2)
        self.assertEqual(len(spotify.sp.playlist_items("Pl100")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl100", max_playlist_length=4)
        self.assertEqual(len(spotify.sp.playlist_items("Pl100")['items']), 0)

    def test_get_artist_albums(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        # Fake Field
        self.assertEqual(spotify.get_artist_albums('Ar002', info=['fake field']), [{'fake field': None}])
        # Fake Artist
        self.assertEqual(spotify.get_artist_albums('Fake Artist'), [])
        # Fake Album Type
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=['fake type']), [])
        # No Info Given
        self.assertEqual(spotify.get_artist_albums('Ar002', info=[]), [{}])
        # No Album Types Given
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=[]), [])
        # Artist With No Albums
        self.assertEqual(spotify.get_artist_albums('Ar001'), [])
        # Default 'albums' Search
        self.assertEqual(spotify.get_artist_albums('Ar002'), [{'id': 'Al002'}])
        # Artist Has Albums But Not Of This Type
        self.assertEqual(spotify.get_artist_albums('Ar003', album_types=['single']), [])
        # Including Multiple Album Types (All Exist)
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=['album', 'single']), 
                         [{'id': 'Al002'}, {'id': 'Al003'}])
        # Including Multiple Album Types (Some Exist)
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=['album', 'single', 'appears_on']), 
                         [{'id': 'Al002'}, {'id': 'Al003'}])
        # Different Album Type
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=['compilation']), [{'id': 'Al004'}])
        # Various Album Types
        self.assertEqual(spotify.get_artist_albums('Ar002', album_types=['album', 'single', 'compilation'], 
                                                   info=['id', 'name']), 
                         [{'id': 'Al002', 'name': 'Fake Album 2'}, 
                          {'id': 'Al003', 'name': 'Fake Album 3'}, 
                          {'id': 'Al004', 'name': 'Fake Album 4'}])
        
        # Add an appears on to an album the artist has creds for
        next(album for album in spotify.sp.env_albums if album['id'] == 'Al006')['album_group'] = 'appears_on'
        # Appears_on album doesn't show up
        self.assertEqual(spotify.get_artist_albums('Ar004'), [{'id': 'Al007'}, {'id': 'Al008'}])
        # Appears_on does show up
        self.assertEqual(spotify.get_artist_albums('Ar004', album_types=['appears_on']), [{'id': 'Al006'}])
        # Artist with full Creds On Shared Album
        self.assertEqual(spotify.get_artist_albums('Ar005'), [{'id': 'Al008'}, {'id': 'Al010'}])
    
    def test_gather_tracks_by_artist(self):
        # Don't really need to test the start and end date since we test 'get_elements_in_date_range' well.
        # Can't do this until 'verify_appears_on_tracks' is mocked. BRO-76
        print("\n\tNot Implemented")

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ALBUMS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TODO Difference betwen album artist data and track artist data
    def test_get_albums_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)

        # Non Existant Album ID
        with self.assertRaises(Exception): spotify.get_albums_tracks(['FakeAlbumId'])
        # No Albums
        self.assertEqual(spotify.get_albums_tracks([]), [])
        # No Album Info
        self.assertEqual(spotify.get_albums_tracks(['Al003'], album_info=[]), 
                         [{'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr003'}]}])
        # No Track Info
        self.assertEqual(spotify.get_albums_tracks(['Al003'], track_info=[]), 
                         [{'id': 'Al003', 'tracks': [{'artists': [{'id': 'Ar002'}]}]}])
        # No Artist Info
        self.assertEqual(spotify.get_albums_tracks(['Al003'], artist_info=[]),
                         [{'id': 'Al003', 'tracks': [{'artists': [{}], 'id': 'Tr003'}]}])
        # No Info At All
        self.assertEqual(spotify.get_albums_tracks(['Al003'], album_info=[], track_info=[], artist_info=[]), 
                         [{'tracks': [{'artists': [{}]}]}])
        # Empty Album
        self.assertEqual(spotify.get_albums_tracks(['Al001']), [{'id': 'Al001', 'tracks': []}])
        # Single Track ALbum
        self.assertEqual(spotify.get_albums_tracks(['Al003']), 
                         [{'id': 'Al003', 
                        'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr003'}]}])
        # Multi Track Album
        self.assertEqual(spotify.get_albums_tracks(['Al002']), 
                         [{'id': 'Al002',
                        'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr001'},
                                 {'artists': [{'id': 'Ar002'}], 'id': 'Tr002'}]}])
        # Multi Track Album, Differing Album Info
        self.assertEqual(spotify.get_albums_tracks(['Al002'], album_info=['id', 'name']), 
                         [{'id': 'Al002',
                        'name': "Fake Album 2",
                        'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr001'},
                                   {'artists': [{'id': 'Ar002'}], 'id': 'Tr002'}]}])
        # Multi Track Album, Differing Album Info and Track Info
        self.assertEqual(spotify.get_albums_tracks(['Al002'], album_info=['id', 'name'], track_info=['id', 'name']), 
                         [{'id': 'Al002',
                        'name': "Fake Album 2",
                        'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr001', 'name': 'Fake Track 1'},
                                   {'artists': [{'id': 'Ar002'}], 'id': 'Tr002', 'name': 'Fake Track 2'}]}])
        # Multi Track Album, Differing Artist Info and Track Info
        self.assertEqual(spotify.get_albums_tracks(['Al002'], artist_info=['id', 'name'], track_info=['id', 'name']), 
                         [{'id': 'Al002',
                        'tracks': [{'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}], 
                                    'id': 'Tr001', 'name': 'Fake Track 1'},
                                   {'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}],
                                    'id': 'Tr002', 'name': 'Fake Track 2'}]}])
        # Album With Tracks Having Multiple Artists
        self.assertEqual(spotify.get_albums_tracks(['Al010']), 
                         [{'id': 'Al010',
                        'tracks': [{'artists': [{'id': 'Ar005'}], 'id': 'Tr014'},
                                   {'artists': [{'id': 'Ar005'}, {'id': 'Ar004'}], 'id': 'Tr015'}]}])
        # Multiple Albums
        self.assertEqual(spotify.get_albums_tracks(['Al010', "Al003"]), 
                         [{'id': 'Al010',
                           'tracks': [{'artists': [{'id': 'Ar005'}], 'id': 'Tr014'},
                                   {'artists': [{'id': 'Ar005'}, {'id': 'Ar004'}], 'id': 'Tr015'}]},
                          {'id': 'Al003', 
                           'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr003'}]}])
        # Multiple Albums Differing Album Info
        self.assertEqual(spotify.get_albums_tracks(['Al010', "Al003"], album_info=['id', 'name']), 
                         [{'id': 'Al010',
                           'name': 'Fake Album 10',
                           'tracks': [{'artists': [{'id': 'Ar005'}], 'id': 'Tr014'},
                                   {'artists': [{'id': 'Ar005'}, {'id': 'Ar004'}], 'id': 'Tr015'}]},
                          {'id': 'Al003', 
                           'name': 'Fake Album 3',
                           'tracks': [{'artists': [{'id': 'Ar002'}], 'id': 'Tr003'}]}])

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACKS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test_get_track_artists(self):
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)
        
        # Test for invalid inputs
        with self.assertRaises(Exception): spotify.get_track_artists("", info="")
        with self.assertRaises(Exception): spotify.get_track_artists("1", info=["id"])
        with self.assertRaises(Exception): spotify.get_track_artists("Pl001", info=[""])
        with self.assertRaises(Exception): (spotify.get_track_artists('non_existent_id'))
        with self.assertRaises(KeyError): spotify.get_track_artists('Tr001', info=['id', 'non_existent_key'])

        self.assertEqual(spotify.get_track_artists('Tr001', info=['id']), [['Ar002']])
        self.assertEqual(spotify.get_track_artists('Tr001', info=['name']), [['Fake Artist 2']]) 
        self.assertEqual(spotify.get_track_artists('Tr001', info=['id', 'name']), [['Ar002', 'Fake Artist 2']])
        self.assertEqual(spotify.get_track_artists('Tr001', info=[]), [[]])
        
        self.assertEqual(spotify.get_track_artists('Tr007', info=['id']), [['Ar003'], ['Ar004']])
        self.assertEqual(spotify.get_track_artists('Tr007', info=['id', 'name']), [['Ar003', 'Fake Artist 3'], 
                                                                                   ['Ar004', 'Fake Artist 4']])

    def test_verify_appears_on_tracks(self):
        # TODO BRO-76: We will need search functionality mocked for this.
        print("\n\tNot Implemented")

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MISC HELPERS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def test_get_track_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)

        self.assertEqual(spotify.get_track_data('Tr001', info=['name']), ['Fake Track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['id', 'name']), ['Tr001', 'Fake Track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['artists']), 
                         [[{'id': 'Ar002', 'name': 'Fake Artist 2'}]])

    def test_get_artist_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)

        self.assertEqual(spotify.get_artist_data('Ar001', info=['name']), ['Fake Artist 1'])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['id', 'name']), ['Ar001', 'Fake Artist 1'])

    def test_get_album_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        spotify._scopes = list(Settings.MAX_SCOPE_LIST)
        thelp.create_env(spotify)

        self.assertEqual(spotify.get_album_data('Al001', info=['name']), ['Fake Album 1'])
        self.assertEqual(spotify.get_album_data('Al001', info=['id', 'name']), ['Al001', 'Fake Album 1'])
        self.assertEqual(spotify.get_album_data('Al001', info=['artists']), [[]])
        self.assertEqual(spotify.get_album_data('Al002', info=['artists']), 
                         [[{'id': 'Ar002', 'name': 'Fake Artist 2'}]])
        self.assertEqual(spotify.get_album_data('Al006', info=['artists']), 
                         [[{'id': 'Ar003', 'name': 'Fake Artist 3'}
                         , {'id': 'Ar004', 'name': 'Fake Artist 4'}]])

    def test_get_playlist_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        thelp.create_env(spotify)

        self.assertEqual(spotify.get_playlist_data('Pl001', info=['name']), ['Fake Playlist 1'])
        self.assertEqual(spotify.get_playlist_data('Pl001', info=['id', 'name']), ['Pl001', 'Fake Playlist 1'])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════