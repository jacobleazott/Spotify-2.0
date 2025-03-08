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
#
# Non-Playable Tracks Sanity Test -
#   - Based off of the 'preview_url' in a track but goal is to make sure every song in our main playlist is 'playable'
#       since Spotify just 'grays' them out without notification.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging

from pprint import PrettyPrinter

from src.helpers.Database_Helpers import DatabaseHelpers
from src.helpers.decorators       import *
from src.helpers.Settings         import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Collection of sanity tests to verify integrity and completion of the user's collections. This is very
             dependent on having a library setup in my fashion.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SanityTest(LogAllMethods):
    # List of tracks to disregard for our comparisons, this currently includes our "shuffle macro" as well as our 
    #   "Soundtracks" playlists tracks
    individual_artist_playlists = []
    years_playlists = []
    master_playlist = []
    user_playlists = []
    user_followed_artists = []

    def __init__(self, logger: logging.Logger=None) -> None:
        self.track_list_to_disregard = list(Settings.MACRO_LIST) 
        self.logger = logger if logger is not None else logging.getLogger()
        self.dbh = DatabaseHelpers(self.logger)
        
        self._gather_playlist_data()
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # "HELPER" FUNCTIONS ══════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Grabs all '__', year, master, and track disregard playlists for later internal use.
    INPUT: N/A
    OUTPUT: N/A
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
                
            if playlist['id'] == Settings.MASTER_MIX_ID:
                self.master_playlist.append({'name': playlist['name'], 'tracks': tracks})
                
            if playlist['id'] in Settings.PLAYLIST_IDS_NOT_IN_ARTISTS:
                self.track_list_to_disregard += [track['id'] for track in tracks]
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Given a list of tracks, find any duplicates. Only works with 'id'.
    INPUT: tracks - List of track dictionary objects.
    OUTPUT: List of string formatted track duplicates.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _find_duplicates(self, tracks):
        duplicates = []
        checked_ids, duplicate_ids = set(), set()

        for track in tracks:
            if track['id'] in checked_ids and track['id'] not in duplicate_ids:
                artist_names = [artist['name'] for artist in self.dbh.db_get_track_artists(track['id'])]
                duplicates.append({'Track': track['name'], 'Artists': artist_names})
                duplicate_ids.add(track['id'])
            checked_ids.add(track['id'])

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
                res_list.append({'Track': track['name'], 'Artists': artist_names})
        
        return res_list
                
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # SANITY CHECKS ═══════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Comparison sanity test for our 3 playlist sets. ie tracks in master but not years etc...
    INPUT: N/A
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
    INPUT: N/A
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
    INPUT: N/A
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
    INPUT: N/A
    OUTPUT: List of string formatted missing tracks from specified playlists.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""  
    def sanity_contributing_artists(self):
        res_list, checked_track_ids = [], set()

        followed_artist_names = {artist['name'] for artist in self.user_followed_artists}
        artist_playlists = {playlist['name']: {track['id'] for track in playlist['tracks']} 
                            for playlist in self.individual_artist_playlists}

        for playlist in self.individual_artist_playlists:
            for track in playlist['tracks']:
                if track['id'] in checked_track_ids:
                    continue
                checked_track_ids.add(track['id'])
                # Get track artists and filter for followed ones (excluding the current playlist owner)
                track_artists = self.dbh.db_get_track_artists(track['id'])
                valid_artists = [artist['name'] for artist in track_artists if artist['name'] in followed_artist_names 
                                 and artist['name'] != playlist['name']]

                # Find missing playlists for valid artists
                missing_artists = [artist for artist in valid_artists 
                                   if track['id'] not in artist_playlists.get(artist, set())]

                if missing_artists:
                    res_list.append({
                        'Track': track['name'],
                        'Artists': [artist['name'] for artist in track_artists],
                        'Missing': missing_artists
                    })

        return res_list
            
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Goes through a '__' playlist to determine if every track in that playlist has the supporting artist of 
                 that specific playlist.
    INPUT: N/A
    OUTPUT: List of tracks that do not belong in varying playlists.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def sanity_artist_playlist_integrity(self):
        res_list = []

        for playlist in self.individual_artist_playlists:
            tracks = []
            for track in playlist['tracks']:
                artists = self.dbh.db_get_track_artists(track['id'])
                if not any(playlist['name'] == artist['name'] for artist in artists):
                    tracks.append({'Track': track['name'], 'Artists': [artist['name'] for artist in artists]})

            if tracks:
                res_list.append({'Playlist': playlist['name'], 'Tracks': tracks})

        return res_list


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Goes through all of our tracks and lets us know if a track is no longer 'playable' by Spotify.
    INPUT: N/A
    OUTPUT: List of tracks that cannot be currently played but are not local.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def sanity_playable_tracks(self) -> list[dict]:
        res_list = []
        
        for track in self.master_playlist[0]['tracks']:
            if not track['is_playable'] and not track['is_local']:
                artist_names = [artist['name'] for artist in self.dbh.db_get_track_artists(track['id'])]
                res_list.append({'Track': track['name'], 'Artists': artist_names})
                
        return res_list
            
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MISC  ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def run_suite(self) -> None:
        pp = PrettyPrinter(width=150)
        print("Playlist Collection Differences ========")
        pp.pprint(self.sanity_diffs_in_major_playlist_sets())
        print("Current In Progress Artists ============")
        pp.pprint(self.sanity_in_progress_artists())
        print("Duplicates =============================")
        pp.pprint(self.sanity_duplicates())
        print("Contributing Artists ===================")
        pp.pprint(self.sanity_contributing_artists())
        print("Artist Playlist Integrity ==============")
        pp.pprint(self.sanity_artist_playlist_integrity())
        print("Non-Playable Tracks ====================")
        pp.pprint(self.sanity_playable_tracks())
        

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════