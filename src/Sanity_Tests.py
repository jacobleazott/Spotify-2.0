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
import General_Spotify_Helpers as gsh
import re

PLAYLIST_IDS_FOR_IGNORED_TRACKS = ["7Mgr45oWF0fzRzdlz0NNgT"]

SCOPE = ["user-follow-read"
       , "playlist-read-collaborative"
       , "playlist-read-private"]    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SanityTest:
    spotify = None
    user_playlists = None
    user_followed_artists = None
    # List of tracks to disregard for our comparisons, this currently includes our "shuffle macro" as well as our 
    #   "Soundtracks" playlists tracks
    track_list_to_disregard = [gsh.SHUFFLE_MACRO_ID]
    individual_artist_playlists = []
    years_playlists = []
    master_playlist = []
    
    def __init__(self):
        self.spotify = gsh.GeneralSpotifyHelpers(SCOPE)
        self.user_playlists = self.spotify.get_user_playlists(info=["id", "name"])
        self.user_followed_artists = self.spotify.get_user_artists(info=["name", "id"])
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
        for playlist in self.user_playlists:
            if playlist["name"].startswith('__'):
                # print(f"Grabbing {playlist['name']}")
                self.individual_artist_playlists.append((playlist['name'][2:], 
                                                         self._get_playlist_tracks_info(playlist["id"])))
                
            if playlist["name"].startswith('20'):
                # print(f"Grabbing {playlist['name']}")
                self.years_playlists.append((playlist['name'], self._get_playlist_tracks_info(playlist["id"])))
                
            if playlist["name"].startswith('The Good - Master Mix'):
                # print(f"Grabbing {playlist['name']}")
                self.master_playlist.append((playlist['name'], self._get_playlist_tracks_info(playlist["id"])))
                
            if playlist["id"] in PLAYLIST_IDS_FOR_IGNORED_TRACKS:
                self.track_list_to_disregard += [track[0] for track in self._get_playlist_tracks_info(playlist["id"])]

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Wrapper on get_playlist_tracks from gsh. Simply to help formatting to compare.
    INPUT: playlist_id - Id for the playlist we want tracks from.
    OUTPUT: Returns a list of the 'id', 'name' and 'artists' 'name' and 'id' of the tracks from the playlist.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _get_playlist_tracks_info(self, playlist_id):
        tracks = self.spotify.get_playlist_tracks(playlist_id
                                             , track_info=["id", "name"]
                                             , artist_info=["id", "name"])
        return [[x["id"], x["name"], x["artists"]] for x in tracks]
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Given a list of tracks, find any duplicates. Only works with 'id'.
    INPUT: tracks - List of track dictionary objects.
    OUTPUT: List of string formatted track duplicates.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _find_duplicates(self, tracks):
        duplicates = []
        checked_list = []
        
        for track in tracks:
            # If track isn't local, already checked, not a double duplicate, and not our shuffle macro
            if track[0] != None and track[0] in checked_list and track not in duplicates \
                    and track[0] != gsh.SHUFFLE_MACRO_ID:
                duplicates.append(track)
                continue
            checked_list.append(track[0])
            
        return [f"{str(dupe[1])} -- {str(dupe[2][0]['name'])}" for dupe in duplicates]

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
            if disregard_tracks and track[0] in self.track_list_to_disregard: continue
            if track not in to_verify_track_list: res_list.append(f"{str(track[1])} -- {str(track[2][0]['name'])}")
        
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
        tmp_list_1 = []
        tmp_list_2 = []
        
        # Prep track collections
        years_track_list = [track for playlist in self.years_playlists for track in playlist[1]]
        # print(years_track_list)
        master_track_list = [track for playlist in self.master_playlist for track in playlist[1]]
        # print(self.master_playlist)
        
        individual_artists_track_list = []
        # Skip any '__' playlist that we aren't following yet as we don't expect them to be in years or master
        for playlist in self.individual_artist_playlists:
            if not any(playlist[0] == artist["name"] for artist in self.user_followed_artists): continue
            individual_artists_track_list += playlist[1]
        
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
            if playlist['name'].startswith("__") and not any(playlist['name'][2:] == artist["name"] 
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
            tmp_dupe_list = self._find_duplicates(playlist[1])
            if len(tmp_dupe_list) > 0: res_list.append((playlist[0], tmp_dupe_list))
            
        # Find duplicates in entire year collection
        tmp_years_dupe_list = self._find_duplicates([track for playlist in self.years_playlists 
                                                     for track in playlist[1]])
        
        if len(tmp_years_dupe_list) > 0: res_list.append(("YEARS COLLECTION", tmp_years_dupe_list))
            
        return res_list
      
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Goes through all combined '__' tracks and finds any that should be in more playlists. ie. tracks that
                 have multiple contributing artists we follow should be in every single one of those '__' playlists.
    INPUT: NA
    OUTPUT: List of string formatted missing tracks from specified playlists.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""  
    def sanity_contributing_artists(self):
        res_list = []
        checked_list = []
        # track_list = [track for track in playlist[1] for playlist in self.individual_artist_playlists]
        for playlist in self.individual_artist_playlists:
            for track in playlist[1]:
                # Find Number of artists I follow in the list of artists for this track
                artist_list = [artist["name"] for artist in track[2] if any(artist["id"] == followed_artist["id"] 
                                                for followed_artist in self.user_followed_artists)]
                if playlist[0] in artist_list: artist_list.remove(playlist[0])
                
                if len(artist_list) > 0:
                    if track[0] in checked_list: continue
                    checked_list.append(track[0])

                    # Go find all the artist playlists in the artist_list
                    for check_playlist in self.individual_artist_playlists:
                        if check_playlist[0] in artist_list:
                            if track[0] not in [tmp_track[0] for tmp_track in check_playlist[1]]:
                                res_list.append(f"{track[1]} - {track[2][0]['name']} = IS MISSING FROM = \
                                                __{check_playlist[0]}")

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
            for track in playlist[1]:
                valid_track = False
                for artist in track[2]:
                    if playlist[0] == artist["name"]:
                        valid_track = True
                        break
                if not valid_track:
                    res_list.append(f"__{playlist[0]} == {track[1]} - {track[2][0]['name']}")

        return res_list
            
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MISC  ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def print_the_results(self):
        print("unimplemented")

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════