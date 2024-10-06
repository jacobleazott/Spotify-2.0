# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS FOR GSH                       CREATED: 2024-09-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Here we unit test all functionality out of 'General_Spotify_Helpers'.
# Run Command - (-v can be passed AFTER the file if verbose mode is desired)
#   python test_General_Spotify_Helper.py 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import inspect
import os
import sys
import unittest
from datetime import datetime, timedelta
from pprint import pprint

import api_response_test_messages as artm
# Override 'spotipy' with our local 'mocked_spotipy.py' MUST BE DONE BEFORE GSH
sys.modules['spotipy'] = __import__('mocked_spotipy')

import General_Spotify_Helpers as gsh


def create_artist(artist_id, name):
    return {
        'id': artist_id,
        'name': name
    }

def create_album(album_id, name, artists, album_type):
    return {
        'id': album_id,
        'name': name,
        'artists': artists,
        'album_type': album_type   # "album", "single", "compilation"
    }

def create_track(track_id, name, album, artists, is_local: bool=False):
    return {
        'id': track_id,
        'name': name,
        'album': album,
        'artists': artists,
        'is_local': is_local
    }
    
def create_playlist(playlist_id, name, description, tracks):
    return {
        'id': playlist_id,
        'name': name,
        'description': description,
        'tracks': tracks                # Note this isn't actually part of the playlist obj
    }
    
    
def create_env(spotify_mocked):
    # Create Artists
    artist_no_tracks = create_artist('Ar001', 'Fake Artist 1')
    artist_only_theirs = create_artist('Ar002', 'Fake Artist 2')
    artist_followed = create_artist('Ar003', 'Fake Artist 3')
    artist_followed_appears_on = create_artist('Ar004', 'Fake Artist 4')
    artist_unfollowed_appears_on = create_artist('Ar005', 'Fake Artist 5')
    
    spotify_mocked.sp.artists += [artist_no_tracks, artist_only_theirs, artist_followed, artist_followed_appears_on, artist_unfollowed_appears_on]
    spotify_mocked.sp.user_artists += [artist_only_theirs, artist_followed, artist_followed_appears_on]
    
    # Create Albums
    al001 = create_album('Al001', 'Fake Album 1', [], 'album')
    al002 = create_album('Al002', 'Fake Album 2', [artist_only_theirs], 'album')
    al003 = create_album('Al003', 'Fake Album 3', [artist_only_theirs], 'single')
    al004 = create_album('Al004', 'Fake Album 4', [artist_only_theirs], 'compilation')
    
    al005 = create_album('Al005', 'Fake Album 5', [artist_followed], 'album')
    al006 = create_album('Al006', 'Fake Album 6', [artist_followed, artist_followed_appears_on], 'album')
    
    al007 = create_album('Al007', 'Fake Album 7', [artist_followed_appears_on], 'album')
    al008 = create_album('Al008', 'Fake Album 8', [artist_followed_appears_on, artist_unfollowed_appears_on], 'album')
    
    al009 = create_album('Al009', 'Fake Album 8', [artist_unfollowed_appears_on], 'single')
    al010 = create_album('Al010', 'Fake Album 10', [artist_unfollowed_appears_on], 'album')
    
    spotify_mocked.sp.env_albums += [al001, al002, al003, al004, al005, al006, al007, al008, al009, al010]

    # Create Tracks
    local_artist = create_artist(None, 'Fake Local Artist 1')
    local_album = create_album(None, 'Fake Local Album 1', [], None)
    local_track = create_track(None, 'Fake Local Track 1', local_album, [local_artist], is_local=True)
    
    tr001 = create_track('Tr001', 'Fake Track 1', al002, [artist_only_theirs])
    tr002 = create_track('Tr002', 'Fake Track 2', al002, [artist_only_theirs])
    tr003 = create_track('Tr003', 'Fake Track 3', al003, [artist_only_theirs])
    tr004 = create_track('Tr004', 'Fake Track 4', al004, [artist_only_theirs])
    
    tr005 = create_track('Tr005', 'Fake Track 5', al005, [artist_followed])
    tr006 = create_track('Tr006', 'Fake Track 6', al006, [artist_followed])
    tr007 = create_track('Tr007', 'Fake Track 7', al006, [artist_followed, artist_followed_appears_on])
    
    tr008 = create_track('Tr008', 'Fake Track 8', al007, [artist_followed_appears_on])
    tr009 = create_track('Tr009', 'Fake Track 9', al007, [artist_followed_appears_on])
    tr010 = create_track('Tr010', 'Fake Track 10', al008, [artist_followed_appears_on])
    tr011 = create_track('Tr011', 'Fake Track 11', al008, [artist_unfollowed_appears_on])
    tr012 = create_track('Tr012', 'Fake Track 12', al008, [artist_followed_appears_on, artist_unfollowed_appears_on])
    
    tr013 = create_track('Tr013', 'Fake Track 13', al009, [artist_unfollowed_appears_on])
    tr014 = create_track('Tr014', 'Fake Track 14', al010, [artist_unfollowed_appears_on])
    tr015 = create_track('Tr015', 'Fake Track 15', al010, [artist_unfollowed_appears_on, artist_followed_appears_on])

    spotify_mocked.sp.tracks += [local_track, tr001, tr002, tr003, tr004, tr005, tr006, tr007, tr008, tr009, tr010, tr011, tr012, tr013, tr014, tr015]

    # Create Playlists
    spotify_mocked.sp.playlists.append(create_playlist('Pl001', 'Fake Playlist 1', 'description 1', []))
    spotify_mocked.sp.playlists.append(create_playlist('Pl002', 'Fake Playlist 2', 'description 2', [tr002, tr003, tr004]))
    spotify_mocked.sp.playlists.append(create_playlist('Pl003', 'Fake Playlist 3', 'description 3', [tr008, tr011, tr012, tr015]))
    spotify_mocked.sp.playlists.append(create_playlist('Pl004', 'Fake Playlist 4', 'description 4', [local_track, local_track, tr001, tr001]))


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
        with self.assertRaises(Exception): gsh.get_generic_field({"test": 1}, None)
        with self.assertRaises(KeyError):  gsh.get_generic_field({"test": 1}, ["id"])
        
        self.assertEqual(gsh.get_generic_field({"test": 1}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["test"]), [1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "test"]), ["weak", 1])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, ["id", "id"]), ["weak", "weak"])
        self.assertEqual(gsh.get_generic_field({"test": 1, "id": "weak"}, []), [])
        self.assertEqual(gsh.get_generic_field({"test": {}, "id": []}, ["test", "id"]), [{}, []])
        self.assertEqual(gsh.get_generic_field({"test": {"world": 2}, "id": ["val1", "val2"]}, ["test", "id"]), [{"world": 2}, ["val1", "val2"]])
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
        test_scopes = [ "user-read-private"
                        , "playlist-modify-public"
                        , "playlist-modify-private"
                        , "user-library-read"]
        
        spotify = gsh.GeneralSpotifyHelpers(scopes=test_scopes)

        with self.assertRaises(Exception): spotify._validate_scope()
        with self.assertRaises(Exception): spotify._validate_scope("user-read-private")
        with self.assertRaises(Exception): spotify._validate_scope(["invalid-scope"])
        with self.assertRaises(Exception): spotify._validate_scope(["user-read-private", "invalid-scope", "playlist-modify-private"])
        
        spotify._validate_scope([])
        spotify._validate_scope(["user-read-private", "playlist-modify-public"])
        spotify._validate_scope(["user-library-read"])
        spotify._validate_scope(["user-read-private", "playlist-modify-public", "playlist-modify-private", "user-library-read"])
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # CLASS FUNCTIONS ═════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def test_get_user_artists(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
        with self.assertRaises(Exception): spotify.remove_all_playlist_tracks("Pl002")
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
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
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
        create_env(spotify)
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
        # Adding Duplicate Tracks
        spotify.add_unique_tracks_to_playlist("Pl001", ["Tr001", "Tr002", "Tr004"])
        tracks = [track['id'] for track in spotify.get_playlist_tracks("Pl001")]
        self.assertEqual(tracks, ["Tr001", "Tr002", "Tr004"])
        
    def test_get_playlist_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
        
        # Empty Playlist
        self.assertEqual(spotify.get_playlist_tracks("Pl001"), [])
        # "Regular" Playlist Default Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002"), 
                         [{'album_id': 'Al002', 'artists': [{'id': 'Ar002'}], 'id': 'Tr002'},
                          {'album_id': 'Al003', 'artists': [{'id': 'Ar002'}], 'id': 'Tr003'},
                          {'album_id': 'Al004', 'artists': [{'id': 'Ar002'}], 'id': 'Tr004'}])
        # No Track Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[]), 
                         [{'album_id': 'Al002', 'artists': [{'id': 'Ar002'}]},
                          {'album_id': 'Al003', 'artists': [{'id': 'Ar002'}]},
                          {'album_id': 'Al004', 'artists': [{'id': 'Ar002'}]}])
        # No Track or Artist Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[], artist_info=[]), 
                         [{'album_id': 'Al002', 'artists': [{}]},
                          {'album_id': 'Al003', 'artists': [{}]},
                          {'album_id': 'Al004', 'artists': [{}]}])
        # No Track, Artist, or Album Info
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=[], artist_info=[], album_info=[]), 
                         [{'artists': [{}]},
                          {'artists': [{}]},
                          {'artists': [{}]}])
        # Different Info From Default
        self.assertEqual(spotify.get_playlist_tracks("Pl002", track_info=['name'], artist_info=['name'], album_info=['name']), 
                         [{'album_name': 'Fake Album 2', 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 2'},
                          {'album_name': 'Fake Album 3', 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 3'},
                          {'album_name': 'Fake Album 4', 'artists': [{'name': 'Fake Artist 2'}], 'name': 'Fake Track 4'}])
        # Duplicate Tracks and Local Tracks Default Info
        self.assertEqual(spotify.get_playlist_tracks("Pl004"), 
                         [{'album_id': None, 'artists': [{'id': None}], 'id': None},
                          {'album_id': None, 'artists': [{'id': None}], 'id': None},
                          {'album_id': 'Al002', 'artists': [{'id': 'Ar002'}], 'id': 'Tr001'},
                          {'album_id': 'Al002', 'artists': [{'id': 'Ar002'}], 'id': 'Tr001'}])
        # Duplicate Tracks and Local Tracks Extra Info
        self.assertEqual(spotify.get_playlist_tracks("Pl004", track_info=['id', 'name'], artist_info=['id', 'name'], album_info=['id', 'name']), 
                         [{'album_id': None, 'album_name': 'Fake Local Album 1', 'artists': [{'id': None, 'name': 'Fake Local Artist 1'}], 'id': None, 'name': 'Fake Local Track 1'},
                          {'album_id': None, 'album_name': 'Fake Local Album 1', 'artists': [{'id': None, 'name': 'Fake Local Artist 1'}], 'id': None, 'name': 'Fake Local Track 1'},
                          {'album_id': 'Al002', 'album_name': 'Fake Album 2', 'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}], 'id': 'Tr001', 'name': 'Fake Track 1'},
                          {'album_id': 'Al002', 'album_name': 'Fake Album 2', 'artists': [{'id': 'Ar002', 'name': 'Fake Artist 2'}], 'id': 'Tr001', 'name': 'Fake Track 1'}])
        
    def test_create_playlist(self):
        spotify = gsh.GeneralSpotifyHelpers()
        
        empty_id = spotify.create_playlist("")
        self.assertEqual(spotify.get_playlist_data(empty_id, info=['name', 'description']), ["", ""])
        
        empty_desc_id = spotify.create_playlist("", description="")
        self.assertEqual(spotify.get_playlist_data(empty_desc_id, info=['name', 'description', 'public']), ["", "", False])
        
        public_true_id = spotify.create_playlist("Test", public=True)
        self.assertEqual(spotify.get_playlist_data(public_true_id, info=['name', 'public']), ["Test", True])

        for count in range(len(spotify.sp.playlists), 410):
            if count < 400:
                self.assertEqual(spotify.create_playlist("Test Playlist", description="tmp"), f"Pl{count:03d}")
            else:
                with self.assertRaises(Exception): spotify.create_playlist("Test Over Count", description="tmp tmp")
                self.assertEqual(len(spotify.sp.playlists), 400)

    def test_change_playlist_details(self):
        spotify = gsh.GeneralSpotifyHelpers()
        
        empty_id = spotify.create_playlist("")
        spotify.change_playlist_details(empty_id, name="Tester")
        self.assertEqual(spotify.get_playlist_data(empty_id, info=['name', 'description']), ["Tester", ""])
        
        playlist_id = spotify.create_playlist("Default", description="set")
        spotify.change_playlist_details(playlist_id, description="Test2")
        self.assertEqual(spotify.get_playlist_data(playlist_id, info=['name', 'description']), ["Default", "Test2"])
        
        playlist_id = spotify.create_playlist("Default", description="set")
        spotify.change_playlist_details(playlist_id, name="Test1", description="Test2")
        self.assertEqual(spotify.get_playlist_data(playlist_id, info=['name', 'description']), ["Test1", "Test2"])
        
    def test_remove_all_playlist_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
        
        with self.assertRaises(Exception): spotify.remove_all_playlist_tracks("Pl002")

        spotify.scopes.append("DELETE-DELETE-DELETE")
        
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002")
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002", max_playlist_length=5)
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        gsh.PLAYLISTS_WE_CAN_DELETE_FROM.append("Pl002")
        
        spotify.remove_all_playlist_tracks("Pl002")
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002", max_playlist_length=2)
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 3)
        
        spotify.remove_all_playlist_tracks("Pl002", max_playlist_length=3)
        self.assertEqual(len(spotify.sp.playlist_items("Pl002")['items']), 0)
        
    def test_get_artist_albums(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
        
        with self.assertRaises(Exception): spotify.get_artist_albums('Ar002', info=['fake field'])
        
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
        
    def test_get_albums_tracks(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)

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

    def test_get_track_artists(self):
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)
        
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
        # We will need search functionality mocked for this, BRO-76
        print("\n\tNot Implemented")
        
    def test_get_track_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)

        self.assertEqual(spotify.get_track_data('Tr001', info=['name']), ['Fake Track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['id', 'name']), ['Tr001', 'Fake Track 1'])
        self.assertEqual(spotify.get_track_data('Tr001', info=['artists']), [[{'id': 'Ar002', 'name': 'Fake Artist 2'}]])
        
    def test_get_artist_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)

        self.assertEqual(spotify.get_artist_data('Ar001', info=['name']), ['Fake Artist 1'])
        self.assertEqual(spotify.get_artist_data('Ar001', info=['id', 'name']), ['Ar001', 'Fake Artist 1'])
        
    def test_get_album_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)

        self.assertEqual(spotify.get_album_data('Al001', info=['name']), ['Fake Album 1'])
        self.assertEqual(spotify.get_album_data('Al001', info=['id', 'name']), ['Al001', 'Fake Album 1'])
        self.assertEqual(spotify.get_album_data('Al001', info=['artists']), [[]])
        self.assertEqual(spotify.get_album_data('Al002', info=['artists']), [[{'id': 'Ar002', 'name': 'Fake Artist 2'}]])
        self.assertEqual(spotify.get_album_data('Al006', info=['artists']), [[{'id': 'Ar003', 'name': 'Fake Artist 3'}
                                                                            , {'id': 'Ar004', 'name': 'Fake Artist 4'}]])
        
    def test_get_playlist_data(self):
        # Don't need to test much since we already unit test 'get_generic_field' extensively
        spotify = gsh.GeneralSpotifyHelpers()
        create_env(spotify)

        self.assertEqual(spotify.get_playlist_data('Pl001', info=['name']), ['Fake Playlist 1'])
        self.assertEqual(spotify.get_playlist_data('Pl001', info=['id', 'name']), ['Pl001', 'Fake Playlist 1'])

        
if __name__ == "__main__":
    unittest.main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════