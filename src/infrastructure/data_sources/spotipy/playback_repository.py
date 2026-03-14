from time import sleep
from typing import Any, Dict, List, Optional

from domain import Playback, Track, AbstractPlaybackRepository

from .track_repository import SpotipyTrackRepository
from .proxy import SpotipyProxy


class SpotipyPlaybackRepository(AbstractPlaybackRepository):

    def __init__(self, spotipy_proxy: SpotipyProxy, track_repository: SpotipyTrackRepository) -> None:
        self.sp = spotipy_proxy
        self.track = track_repository

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_playback(self) -> Playback:
        response = self.sp.current_playback()
        return self.build(response)
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def write_to_queue(self, track_ids: list[str]) -> None:
        for track_id in track_ids:
            self.sp.add_to_queue(track_id)
            # TODO: Probably push this change to the proxy for ALL rate limits
            sleep(0.20)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # TODO: Shuffle Enum? Repeat Enum?
    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        if pause:
            self.sp.pause_playback()
        
        if skip == "next":
            self.sp.next_track()
        elif skip == "prev":
            self.sp.previous_track()
        
        if shuffle:
            self.sp.shuffle(shuffle)
        
        if repeat:
            self.sp.repeat(repeat)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # TODO: Probably need to handle pagination AND before/ after time AND how many tracks
    def get_recent_tracks(self) -> list[Track]:
        response = self.sp.current_user_recently_played(limit=50)
        raise NotImplementedError 

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def build(self, playback_raw: dict) -> Playback:
        if not playback_raw:
            return None
        
        return Playback(
            playlist_id=playback_raw.get("context", {}).get("uri").split(":")[2],
            device_id=playback_raw.get("device", {}).get("id"),
            device_name=playback_raw.get("device", {}).get("name"),
            volume_percent=playback_raw.get("device", {}).get("volume_percent"),
            progress_ms=playback_raw.get("progress_ms"),
            is_playing=playback_raw.get("is_playing"),
            shuffle=playback_raw.get("shuffle_state"),
            smart_shuffle=playback_raw.get("smart_shuffle"),
            repeat=playback_raw.get("repeat_state"),
            timestamp=playback_raw.get("timestamp"),
            track=self.track.build(playback_raw.get("item"))
        )