# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SANITY TESTS                             CREATED: 2024-05-16          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# My spotify stuff is a little complicated. This has caused me to fuck up quite a bit in keeping playlist sets in
#   sync... among other issues. This file is meant to be sanity tests that I can run on my profile to make sure I am
#   not making any mistakes.
#
# Comparison Sanity Test -
#   - Check that all tracks in __ playlists are in year playlists and master, vice versa for the others
#
# Duplicate Sanity Test -
#   - Check for duplicate tracks in collections, ie master, years, __
#   - Checks duplicates in all the years playlists combined
#
# Contributing Artists Sanity Test - 
#   - Check that all supporting artists have ALL tracks in their '__', ie a song by powfu and promoting sounds 
#       should be in both __ playlists
#
# Artist Integrity Sanity Test -
#   - All tracks in a __ playlist have a supporting __ artist for the track
#
# In Progress Sanity Test -
#   - Basically just give the user a list of __ playlists that the user is not following currently
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import re
import sqlite3
from glob import glob

import General_Spotify_Helpers as gsh

from Database_Helpers import DatabaseHelpers
from decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Collection of sanity tests to verify integrity and completion of the user's collections. This is very
             dependent on having a library setup in my fashion.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SanityTest(LogAllMethods):
    FEATURE_SCOPES = ["user-follow-read"
                    , "playlist-read-collaborative"
                    , "playlist-read-private"]
    
    PLAYLIST_IDS_FOR_IGNORED_TRACKS = ["7Mgr45oWF0fzRzdlz0NNgT"]

    # List of tracks to disregard for our comparisons, this currently includes our "shuffle macro" as well as our 
    #   "Soundtracks" playlists tracks
    track_list_to_disregard = gsh.MACRO_LIST
    individual_artist_playlists = []
    years_playlists = []
    master_playlist = []
    user_playlists = []
    user_followed_artists = []

    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        # self.spotify.scopes = self.FEATURE_SCOPES
        self.logger = logger if logger is not None else logging.getLogger()
        
        self.dbh = DatabaseHelpers(self.logger)
        self._gather_playlist_data()
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # "HELPER" FUNCTIONS ══════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Grabs all '__', year, master, and track disregard playlists for later internal use.
    INPUT: NA
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _gather_playlist_data(self):
        self.user_followed_artists = self.dbh.db_get_user_followed_artists()
        self.user_playlists = self.dbh.db_get_user_playlists()
        
        for playlist in self.user_playlists:
            tracks = self.dbh.db_get_tracks_from_playlist(playlist['id'])
            
            if playlist['name'].startswith('__'):
                self.individual_artist_playlists.append({'name': playlist['name'][2:], 'tracks': tracks})
                
            if playlist['name'].startswith('20'):
                self.years_playlists.append({'name': playlist['name'], 'tracks': tracks})
                
            if playlist['name'].startswith('The Good - Master Mix'):
                self.master_playlist.append({'name': playlist['name'], 'tracks': tracks})
                
            if playlist['id'] in self.PLAYLIST_IDS_FOR_IGNORED_TRACKS:
                self.track_list_to_disregard += [track['id'] for track in tracks]
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Given a list of tracks, find any duplicates. Only works with 'id'.
    INPUT: tracks - List of track dictionary objects.
    OUTPUT: List of string formatted track duplicates.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _find_duplicates(self, tracks):
        duplicates, checked_list = [], []

        for track in tracks:
            # If track isn't local, already checked, not a double duplicate, and not our shuffle macro
            if track['id'] != None and track['id'] in checked_list and track not in duplicates \
                    and track['id'] != gsh.SHUFFLE_MACRO_ID:
                artist_names = [artist['name'] for artist in self.dbh.db_get_track_artists(track['id'])]
                duplicates.append(f"{dupe['name']} -- {artist_names}")
                continue
            checked_list.append(track['id'])
            
        return duplicates

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Verifies every track in 'key_track_list' is present in 'to_verify_track_list'. Will ignore 
                 'track_list_to_disregard' if 'disregard_tracks' is True.
    INPUT: key_track_list - List of dictionary tracks to compare against.
           to_verify_track_list - List of dictionary tracks we verify.
           disregard_tracks - Bool whether we want to disregard 'track_list_to_disregard'.
    OUTPUT: List of string formatted tracks that were present in 'key_track_list' but not 'to_verify_track_list'.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _compare_track_lists(self, key_track_list, to_verify_track_list, disregard_tracks=False):
        res_list = []
        
        for track in key_track_list:
            if disregard_tracks and track['id'] in self.track_list_to_disregard: 
                continue
            if track not in to_verify_track_list: 
                artist_names = [artist['name'] for artist in self.dbh.db_get_track_artists(track['id'])]
                res_list.append(f"{track['name']} -- {artist_names}")
        
        return res_list
                
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # SANITY CHECKS ═══════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Comparison sanity test for our 3 playlist sets. ie tracks in master but not years etc...
    INPUT: NA
    OUTPUT: List of collections with their respective tracks that are missing from the varying collections.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def sanity_diffs_in_major_playlist_sets(self):
        res_list = []

        # Prep track collections
        years_track_list = [track for playlist in self.years_playlists for track in playlist['tracks']]
        master_track_list = [track for playlist in self.master_playlist for track in playlist['tracks']]
        
        individual_artists_track_list = []
        # Skip any '__' playlist that we aren't following yet as we don't expect them to be in years or master
        for playlist in self.individual_artist_playlists:
            if not any(playlist['name'] == artist['name'] for artist in self.user_followed_artists): continue
            individual_artists_track_list += playlist['tracks']
        
        # We skip the disregard tracks when comparing against the '__' playlists, we don't care about them
        res_list.append(("TRACKS IN MASTER PLAYLISTS BUT NOT YEAR", 
                         self._compare_track_lists(master_track_list, years_track_list)))
        res_list.append(("TRACKS IN MASTER PLAYLISTS BUT NOT '__'", 
                         self._compare_track_lists(master_track_list, individual_artists_track_list, 
                                                   disregard_tracks=True)))
        res_list.append(("TRACKS IN YEARS PLAYLISTS BUT NOT MASTER", 
                         self._compare_track_lists(years_track_list, master_track_list)))
        res_list.append(("TRACKS IN YEARS PLAYLISTS BUT NOT '__'", 
                         self._compare_track_lists(years_track_list, individual_artists_track_list, 
                                                   disregard_tracks=True)))
        res_list.append(("TRACKS IN '__' PLAYLISTS BUT NOT MASTER", 
                         self._compare_track_lists(individual_artists_track_list, master_track_list)))
        res_list.append(("TRACKS IN '__' PLAYLISTS BUT NOT YEARS", 
                         self._compare_track_lists(individual_artists_track_list, years_track_list)))

        # Just remove any groups that didn't have comparisons to show
        res_list = [res for res in res_list if len(res[1]) > 0]

        return res_list
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Finds any current "in progress" artists just as a sanity check that we do follow all of our 
                 contributing artists.
    INPUT: NA
    OUTPUT: List of '__' playlists that the user currently doesn't follow the artist for.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def sanity_in_progress_artists(self):
        res_list = []
        for playlist in self.user_playlists:
            if playlist['name'].startswith("__") and not any(playlist['name'][2:] == artist['name']
                                                             for artist in self.user_followed_artists):
                res_list.append(f"{playlist['name']}")
        return res_list

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Finds any duplicate tracks (id's) in each of our 3 collections individually and years combined.
    INPUT: NA
    OUTPUT: List of string formatted tracks that are duplicates in their respective collection.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def sanity_duplicates(self):
        res_list = []
        # Find duplicates in every year, '__', and master playlist
        for playlist in self.individual_artist_playlists + self.years_playlists + self.master_playlist:
            tmp_dupe_list = self._find_duplicates(playlist['tracks'])
            if len(tmp_dupe_list) > 0: res_list.append((playlist['name'], tmp_dupe_list))
            
        # Find duplicates in entire year collection
        tmp_years_dupe_list = self._find_duplicates([track for playlist in self.years_playlists 
                                                     for track in playlist['tracks']])
        
        if len(tmp_years_dupe_list) > 0: res_list.append(("YEARS COLLECTION", tmp_years_dupe_list))
            
        return res_list
      
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Goes through all combined '__' tracks and finds any that should be in more playlists. ie. tracks that
                 have multiple contributing artists we follow should be in every single one of those '__' playlists.
    INPUT: NA
    OUTPUT: List of string formatted missing tracks from specified playlists.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""  
    def sanity_contributing_artists(self):
        res_list, checked_list = [], []

        for playlist in self.individual_artist_playlists:
            for track in playlist['tracks']:
                # Find Number of artists I follow in the list of artists for this track
                artist_list = [artist for artist in self.dbh.db_get_track_artists(track['id']) if 
                               any(artist['name'] == f_artist['name'] for f_artist in self.user_followed_artists)]
                
                if playlist['name'] in artist_list: 
                    artist_list.remove(playlist['name'])
                
                if len(artist_list) > 0:
                    if track['id'] in checked_list: 
                        continue
                    checked_list.append(track['id'])
                    # Go find all the artist playlists in the artist_list
                    for check_playlist in self.individual_artist_playlists:
                        if check_playlist['name'] in artist_list and \
                                track['id'] not in [tmp_track['id'] for tmp_track in check_playlist['tracks']]:
                            artist_names = [artist['name'] for artist in self.dbh.db_get_track_artists(track['id'])]
                            res_list.append(f"{track['name']} - {artist_names} = IS MISSING FROM = \
                                            __{check_playlist['name']}")

        return res_list
            
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Goes through a '__' playlist to determine if every track in that playlist has the supporting artist of 
                 that specific playlist.
    INPUT: NA
    OUTPUT: List of tracks that do not belong in varying playlists.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def sanity_artist_playlist_integrity(self):
        res_list = []
        
        for playlist in self.individual_artist_playlists:
            for track in playlist['tracks']:
                valid_track = False
                artists = self.dbh.db_get_track_artists(track['id'])
                for artist in artists:
                    if playlist['name'] == artist['name']:
                        valid_track = True
                        break
                if not valid_track:
                    res_list.append(f"__{playlist['name']} == {track['name']} - {artist_names}")

        return res_list
            
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MISC  ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def print_the_results(self):
        print("unimplemented")
        
        
def main():
    # SpotifyFeatures().generate_monthly_release() #
    # https://open.spotify.com/playlist/6kGQQoelXM2YDOSmqUUzRw?si=2622a7bb129a498a
    # SpotifyFeatures().shuffle_playlist("6kGQQoelXM2YDOSmqUUzRw", shuffle_type=ShuffleType.WEIGHTED)
    spotify = None
    sanity_tester = SanityTest(spotify)
    print(sanity_tester.sanity_diffs_in_major_playlist_sets())
    print(sanity_tester.sanity_in_progress_artists())
    print(sanity_tester.sanity_duplicates())
    print(sanity_tester.sanity_artist_playlist_integrity())
    print(sanity_tester.sanity_contributing_artists())
    

if __name__ == "__main__":
    main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════