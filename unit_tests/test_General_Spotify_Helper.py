# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS FOR GSH                       CREATED: 2024-09-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit Tests
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

from datetime import datetime, timedelta
import unittest
import inspect
import sys
import os

import api_response_test_messages as artm
# Override 'spotipy' with our local 'mocked_spotipy.py' MUST BE DONE BEFORE GSH
sys.modules['spotipy'] = __import__('mocked_spotipy')

sys.path.insert(1, '/home/jaleazo/projects/Spotify_Release_Pi/src')
import General_Spotify_Helpers as gsh


def default_env(spotify):
    for i in range(0, 3):
        artist_tmp = artm.artist_full_test.copy()
        artist_tmp['name'] = f"fake artist {len(spotify.sp.artists)+1}"
        artist_tmp['id'] = f"Ar{(len(spotify.sp.artists)+1):03d}"
        spotify.sp.artists.append(artist_tmp)
        
    for artist in spotify.sp.artists:
        for i in range(0, 5):
            album_tmp = artm.album_test.copy()
            album_tmp['name'] = f"fake album {len(spotify.sp.albums)+1}"
            album_tmp['id'] = f"Al{(len(spotify.sp.albums)+1):03d}"
            album_tmp['artists'] = [artm.full_artist_to_simple(artist)]
            album_tmp['album_type'] = "album" if i < 2 else "compilation" if i >= 4 else "single"
            spotify.sp.albums.append(album_tmp)

    for album in spotify.sp.albums:
        num_tracks = 0
        if album['album_type'] == "single":         num_tracks = 1 
        if album['album_type'] == "compilation":    num_tracks = 2
        if album['album_type'] == "appears_on":     num_tracks = 3 
        if album['album_type'] == "album":          num_tracks = 4 
        
        for i in range(0, num_tracks):
            track_tmp = artm.track_test.copy()
            track_tmp['name'] = f"fake track {len(spotify.sp.tracks)+1}"
            track_tmp['id'] = f"Tr{(len(spotify.sp.tracks)+1):03d}"
            track_tmp['album'] = album.copy()
            track_tmp['artists'] = track_tmp['album']['artists'].copy()
            spotify.sp.tracks.append(track_tmp)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all GSH functionality
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
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
        with self.assertRaises(KeyError):  gsh.get_generic_field({"test": 1}, ["id"])
        
        self.assertEqual(gsh.get_generic_field({"test": 1}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["test", "id"]), [1, "weak"])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "test"]), ["weak", 1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "id"]), ["weak", "weak"])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, []), [])
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
                    assert False
                    print(f"FAILED [Additional Value]: {res}")

            for calc_res in calc_results:
                if calc_res not in results:
                    assert False
                    print(f"FAILED [Missing Value]   : {calc_res}")
                    
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
                                                                 False, False, False, False, True , 
                                                                 False, False, False, True , False, 
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
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # "PRIVATE" CLASS FUNCTIONS ═══════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def test_get_next_response(self):
        print("\n\tNot Implemented")
    
    def test_iterate_and_grab_data(self):
        print("\n\tNot Implemented")
        
    def test_gather_data(self):
        print("\n\tNot Implemented")
        
    def test_validate_scope(self):
        print("\n\tNot Implemented")
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # CLASS FUNCTIONS ═════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
    def test_get_user_artists(self):
        print("\n\tNot Implemented")
        
    def test_get_user_playlists(self):
        print("\n\tNot Implemented")
        
    def test_get_playback_state(self):
        print("\n\tNot Implemented")
        
    def test_write_to_queue(self):
        print("\n\tNot Implemented")
        
    def test_change_playback(self):
        print("\n\tNot Implemented")
        
    def test_add_tracks_to_playlist(self):
        print("\n\tNot Implemented")
        
    def test_add_unique_tracks_to_playlist(self):
        print("\n\tNot Implemented")
        
    def test_get_playlist_tracks(self):
        print("\n\tNot Implemented")
        
    def test_create_playlist(self):
        print("\n\tNot Implemented")
        
    def test_change_playlist_details(self):
        print("\n\tNot Implemented")
        
    def test_remove_all_playlist_tracks(self):
        print("\n\tNot Implemented")
        
    def test_get_artist_albums(self):
        print("\n\tNot Implemented")
        
    def test_gather_tracks_by_artist(self):
        print("\n\tNot Implemented")
        
    def test_get_albums_tracks(self):
        print("\n\tNot Implemented")
        
    def test_get_track_artists(self):
        print("\n\tNot Implemented")
        
    def test_verify_appears_on_tracks(self):
        print("\n\tNot Implemented")
        
    def test_get_track_data(self):
        spotify = gsh.GeneralSpotifyHelpers([])
        default_env(spotify)
        
        with self.assertRaises(Exception): spotify.get_track_data([""], "")
        with self.assertRaises(Exception): spotify.get_track_data("1", ["id"])
        with self.assertRaises(Exception): spotify.get_track_data("Tr001", [""])
        
        self.assertEqual(spotify.get_track_data('Tr001', info=['name']), ['fake track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['id', 'name']), ['Tr001', 'fake track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['disc_number', 'explicit', 'track_number']), [0, False, 0])
        self.assertEqual(spotify.get_track_data('Tr001', info=['id', ['external_ids', 'isrc']]), ['Tr001', 'fake_isrc'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['external_urls']), [{'spotify': 'track_spotify_url'}])
        self.assertEqual(spotify.get_track_data('Tr001', info=['available_markets']), [['US']])
        self.assertEqual(spotify.get_track_data('Tr001', info=[]), [])
        self.assertEqual(spotify.get_track_data('Tr001', info=[]), [])
        
    def test_get_artist_data(self):
        spotify = gsh.GeneralSpotifyHelpers([])
        default_env(spotify)
        
        with self.assertRaises(Exception): spotify.get_artist_data([""], info="")
        with self.assertRaises(Exception): spotify.get_artist_data("1", info=["id"])
        with self.assertRaises(Exception): spotify.get_artist_data("Ar001", info=[""])
        
        self.assertEqual(spotify.get_artist_data('Ar001', info=['name']), ['fake artist 1'])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['id', 'name']), ['Ar001', 'fake artist 1'])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['id', ['followers', 'total']]), ['Ar001', 100000])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['external_urls']), [{'spotify': 'artist_spotify_url'}])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['genres']), [['fake genre 1']])
        self.assertEqual(spotify.get_artist_data('Ar001', info=[]), [])
        
    def test_get_album_data(self):
        print("\n\tNot Implemented")
    
    def test_get_playlist_data(self):
        print("\n\tNot Implemented")

if __name__ == "__main__":
    unittest.main()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════