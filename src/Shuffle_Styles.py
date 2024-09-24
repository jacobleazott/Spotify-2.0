# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    SHUFFLE STYLES                          CREATED: 2021-07-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import random
import logging
import sqlite3
from datetime import datetime
from enum import unique, Enum

from decorators import *
import General_Spotify_Helpers as gsh
from Log_Playback import LogPlayback

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@unique
class ShuffleType(Enum):
    RANDOM = 0
    WEIGHTED = 1

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Shuffler(LogAllMethods):
    QUEUE_LENGTH = 80
    FEATURE_SCOPES = ["playlist-read-private"
                    , "playlist-read-collaborative"
                    , "user-modify-playback-state"]

    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.spotify.scopes = self.FEATURE_SCOPES
        self.logger = logger if not None else logger.getLogger()
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Creates a weighted queue for listening, it orders tracks from least to most listened and 'partially'
                 randomizes the queue based upon how many times specifically we have listened to each track
    INPUT: track_ids - list of tracks we pulled from the playlist and are making the weighted queue off of
    OUTPUT: list of tracks partially randomized in the reverse weighted form
    # TODO: LOOK ABOVE< MIGHT NEED TO FIX
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def make_weighted(track_ids: list[str]):
        track_counts_conn = sqlite3.connect(LogPlayback.TRACK_COUNTS_DB)
        track_count_data = []

        # Grab all the track_counts for our track_ids, we default to 0 listens if we don't find it
        for track_id in track_ids:
            if track_id == gsh.SHUFFLE_MACRO_ID:
                continue
            track_query = track_counts_conn.execute(f"SELECT * FROM 'tracks' WHERE 'tracks'.track_id = '{track_id}'").fetchone()

            if track_query is None:
                track_count_data.append((0, track_id))
            else:
                track_count_data.append((track_query[1], track_id))
        
        track_counts_conn.close()
        track_count_data.sort()
      
        # Below we are going to group same play_count tracks, so we start with [[1, a], [1, b], [4, c], [4, d], [5, e]]
        #   and end with [[a, b], [c, d], [e]]. Once we reach a minimum of QUEUE_LENGTH of total tracks in 
        #   track_count_groupings we exit out since we don't care past that
        tmp_play_count = 0
        tmp_track_count_group = []
        track_count_groupings = []

        for idx, track in enumerate(track_count_data):
            if track[0] > tmp_play_count and len(tmp_track_count_group) > 0:
                track_count_groupings.append(tmp_track_count_group)
                tmp_play_count = track[0]
                tmp_track_count_group = []
                if idx >= QUEUE_LENGTH:
                    break
            tmp_track_count_group.append(track[1])
        track_count_groupings.append(tmp_track_count_group)
            
        # Now we randomize each "set" of track_counts individually and add them up to one master list
        track_list = []
        random.seed(datetime.datetime.now().timestamp())
       
        for track_group in track_count_groupings:
            random.shuffle(track_group)
            track_list += track_group
        
        return track_list[:min(len(track_list), QUEUE_LENGTH)]

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def shuffle(self, playlist_id: str, shuffle_type: ShuffleType) -> None:
        self.spotify.change_playback(skip="next", shuffle=True)
        
        tracks = [track['id'] for track in self.spotify.get_playlist_tracks(playlist_id) 
                  if track['id'] is not None and track['id'] not in gsh.MACRO_LIST]
        
        match shuffle_type:
            case ShuffleType.RANDOM:
                random.seed(datetime.now().timestamp())
                random.shuffle(tracks)
            case ShuffleType.WEIGHTED:
                tracks = self.shuffle_weighted(tracks)
            case _:
                raise Exception(f"Unknown Shuffle Type: {shuffle_type}")
                
                
        tracks = tracks[:(min(len(tracks), QUEUE_LENGTH))]
        self.spotify.write_to_queue(tracks)
    
    




    

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════