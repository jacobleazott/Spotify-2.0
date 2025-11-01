from src.models import Playlist
from src.mappers import map_playlist
from src.sources import SourceBundle

from .service_coordinator import ServiceCoordinator
from .base_service import BaseService

from typing import Any, Dict, List, Optional

class PlaylistService(BaseService[Playlist]):
    def __init__(self, coordinator: ServiceCoordinator) -> None:
        super().__init__(Playlist, coordinator)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _normalize(self, raw_data: dict, source: SourceBundle) -> dict:
        return source.playlist.normalize(raw_data)
    
    def _get_one_from_norm_raw(self, norm_data: dict) -> Playlist:
        if not norm_data:
            return None
        
        playlist = self._get_or_cache(norm_data['id'], lambda: map_playlist(norm_data))

        if norm_data["tracks"]:
            playlist.tracks = self.coordinator.track_service._get_many_from_norm_raw(norm_data["tracks"])
        
        return playlist
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def get_playlist(self, playlist_id: str, prefer_external: bool=True) -> Playlist:
        return self.get_playlists([playlist_id], prefer_external=prefer_external)[0]
        
    def get_playlists(self, playlist_ids: list[str], prefer_external: bool=True) -> list[Playlist]:
        return self._fetch_and_hydrate(
            lambda s: s.playlist.get_playlists(playlist_ids),
            prefer_external
        )

    # TODO: Should we maybe try to get the updated snapshot_id????
    # TODO: Does prefer_external make sense here?
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str], prefer_external: bool=True) -> None:
        source = self._get_source(prefer_external)
        source.playlist.add_tracks_to_playlist(playlist_id, track_ids)
    
    def create_playlist(self, name: str, description: str='', public: bool=False
                        , prefer_external: bool=True) -> Playlist:
        source = self._get_source(prefer_external)
        return self._get_one_from_raw(source.playlist.create_playlist(name, description, public))

    # TODO: Might need to do something different here since we are modifying the cache
    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None
                                , prefer_external: bool=True) -> Playlist:
        source = self._get_source(prefer_external)
        return self._get_one_from_raw(source.playlist.change_playlist_details(playlist_id, name, description))

    # TODO: Might need to do something different here since we are modifying the cache
    # TODO: Are we even caching Playlists?
    def remove_playlist_tracks(self, playlist_id: str, prefer_external: bool=True) -> None:
        source = self._get_source(prefer_external)
        source.playlist.remove_playlist_tracks(playlist_id)


