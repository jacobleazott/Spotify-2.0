# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SHUFFLE STYLES                           CREATED: 2021-07-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Spotify's shuffle sucks... like a lot. This file exists to give the user their own choice in how they want their
#   playlists shuffled. Currently only works with given playlist_id's but may one day be improved to simply take a 
#   collection of 'tracks' to be more dynamic.
#
# SHUFFLE TYPES -
#   RANDOM - ...it's random, like actually random, not spotify's 'random'. (yes yes it's pseudo-random)
#       
#   WEIGHTED - This shuffle type requires the Log_Playback functionality which records the user's playback. From that
#               logging we get a 'track counts db' that contains every song the user has listened to (since it's been
#               running) and how many times they have listened to it. We then sort the entire playlist's contents in
#               order of # of times listened. It grabs the lowest 'QUEUE_LENGTH' tracks (rounding up for ties of 
#               listens). It then 'randomizes' each 'group' of tracks ie. tracks with 1 listen in 1 group, 2 listens
#               in another and so on. This way no track with say 3 listens ends up in the queue before one with 2.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import random
import sqlite3

from datetime import datetime
from enum     import unique, Enum

import src.General_Spotify_Helpers as gsh

from src.helpers.Database_Helpers import DatabaseHelpers
from src.helpers.decorators       import *
from src.helpers.Settings         import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Enum to define our different shuffle styles for playlists.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@unique
class ShuffleType(Enum):
    RANDOM = 0
    WEIGHTED = 1

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Feature class that implements various shuffle methodologies. Currently works only on full playlists.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Shuffler(LogAllMethods):

    def __init__(self, spotify, tcdb_path: str=None, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        self.vault_db = DatabaseHelpers(Settings.LISTENING_VAULT_DB, logger=self.logger)        
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a weighted list of tracks, it orders tracks from least to most listened and 'partially'
                 randomizes the queue based upon how many times specifically we have listened to each track.
    INPUT: track_ids - List of tracks we pulled from the playlist and are making the weighted queue off of.
    OUTPUT: List of tracks partially randomized in the reverse weighted form.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _weighted_shuffle(self, track_ids: list[str]) -> list[str]:
        track_counts = {row['id']: row['play_count'] for row in self.vault_db.get_track_play_counts(track_ids)}
        for track_id in track_ids:
            track_counts[track_id] = track_counts.get(track_id, 0)
        
        track_counts_list = [{'id': k, 'play_count': v} for k, v in track_counts.items()]
        track_counts_list.sort(key=lambda x: x['play_count'])
        
        # Below we are going to group same play_count tracks, so we start with [[1, a], [1, b], [4, c], [4, d], [5, e]]
        #   and end with [[a, b], [c, d], [e]]. Once we reach a minimum of QUEUE_LENGTH of total tracks in 
        #   track_count_groupings we exit out since we don't care past that
        cur_play_count = 0
        tmp_track_count_group, track_count_groupings = [], []

        for idx, track_data in enumerate(track_counts_list):
            if track_data['play_count'] > cur_play_count and len(tmp_track_count_group) > 0:
                track_count_groupings.append(tmp_track_count_group)
                tmp_track_count_group = []
                if idx >= Settings.MAX_QUEUE_LENGTH:
                    break
            tmp_track_count_group.append(track_data['id'])
            cur_play_count = track_data['play_count']
            
        track_count_groupings.append(tmp_track_count_group)
        
        # Now we randomize each "set" of track_counts individually and add them up to one master list
        track_list = []
        random.seed(datetime.now().timestamp())

        for track_group in track_count_groupings:
            random.shuffle(track_group)
            track_list += track_group

        return track_list

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs all the tracks from the given playlist, and applies the given shuffle to those tracks.
                 it then adds those now 'shuffled' tracks to the user's queue.
    INPUT: playlist_id - Id of the playlist we will be grabbing the tracks from.
           shuffle_type - Specific shuffle type we will be applying to the tracks from 'playlist_id'.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    @gsh.scopes(["user-modify-playback-state"])
    def shuffle(self, playlist_id: str, shuffle_type: ShuffleType) -> None:
        self.logger.info(f"Shuffle Type: {shuffle_type}, Playlist: {playlist_id}")
        track_ids = [track['id'] for track in self.vault_db.get_tracks_from_playlist(playlist_id) 
                     if track['id'] not in Settings.MACRO_LIST and not track['is_local']]
        self.logger.info(f"\tFound '{len(track_ids)}' Tracks")
        
        match shuffle_type:
            case ShuffleType.RANDOM:
                random.seed(datetime.now().timestamp())
                random.shuffle(track_ids)
            case ShuffleType.WEIGHTED:
                track_ids = self._weighted_shuffle(track_ids)
            case _:
                raise Exception(f"Unknown Shuffle Type: {shuffle_type}")
        
        if len(track_ids) > 0:
            self.spotify.write_to_queue([track_ids[0]])
            self.spotify.change_playback(shuffle=True)
            self.spotify.write_to_queue(track_ids[1:Settings.MAX_QUEUE_LENGTH])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════