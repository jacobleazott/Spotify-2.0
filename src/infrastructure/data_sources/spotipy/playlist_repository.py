from domain import Playlist, AbstractPlaylistRepository

from .track_repository import SpotipyTrackRepository
from .proxy import SpotipyProxy

from src.common.utils import chunks

from typing import Any, Dict, List, Optional


class SpotipyPlaylistRepository(AbstractPlaylistRepository):
    
    def __init__(self, spotipy_proxy: SpotipyProxy, track_repository: SpotipyTrackRepository) -> None:
        self.sp = spotipy_proxy
        self.track = track_repository

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_playlist(self, playlist_id: str) -> Playlist:
        raw = self.sp.playlist(playlist_id, market="US")
        return self.build(raw)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_playlists(self, playlist_ids: list[str]) -> list[Playlist]:
        playlists = []

        for playlist_id in playlist_ids:
            playlists.append(self.get_playlist(playlist_id))

        return playlists

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def add_tracks_to_playlist(self, track_ids: list[str], playlist_id: str) -> None:
        track_chunks = chunks(track_ids, 100)
        for chunk in track_chunks:
            self.sp.playlist_add_items(playlist_id, chunk)

        # TODO: Anyway to verify this? Specifically without querying the playlist?
        # We do get snapshot_id of the new updated playlist version

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def create_playlist(self, name: str, description: str='', public: bool=False) -> Playlist:
        # TODO: Verify we don't have too many playlists
        response = self.sp.current_user_playlist_create(name, description=description, public=public)()
        return self.build(response)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None) -> None:
        updates = {
            "name": name,
            "description": description
        }
        payload = {k: v for k, v in updates.items() if v is not None}

        if payload:
            self.sp.playlist_change_details(playlist_id, **payload)

        # TODO: Any logging or what not if this fails or not enough args are passed?
        # TODO: Is this the best way to do this? Optional feels like it should work well but I'm not sure

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def remove_playlist_tracks(self, playlist_id: str) -> None:
        # TODO: Where are we putting scope protection? We need to be very very careful
        track_ids = [track["id"] for track in self.track.get_playlist_tracks(playlist_id)]
    
        for track_chunk in chunks(track_ids, 100):
            self.sp.playlist_remove_all_occurrences_of_items(playlist_id, track_chunk)

        # TODO: We also get snapshot id here, care about it?

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def build(self, playlist_raw: dict) -> Playlist:
        if not playlist_raw or not playlist_raw.get("id"):
            return None
        
        tracks = [self.track.build(track) for track in playlist_raw.get("items", {}).get("items", [])]
        
        return Playlist(
            id=playlist_raw["id"],
            name=playlist_raw.get("name"),
            description=playlist_raw.get("description"),
            snapshot_id=playlist_raw.get("snapshot_id", ""),
            collaborative=playlist_raw.get("collaborative"),
            public=playlist_raw.get("public"),
            total_tracks=playlist_raw.get("items", {}).get("total", 0),
            tracks=tracks
        )
