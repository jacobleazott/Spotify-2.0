from domain.models import Track
from infrastructure.mappers import map_track
from domain.repositories import RepoBundle
from domain.core import ServiceCoordinator

from .base_service import BaseService

class TrackService(BaseService[Track]):
    def __init__(self, coordinator: ServiceCoordinator) -> None:
        super().__init__(Track, coordinator)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _normalize(self, raw_data: dict, source: RepoBundle) -> dict:
        return source.track.normalize(raw_data)
    
    def _normalize(self, raw_data: dict, prefer_external: bool) -> dict:
        if prefer_external:
            return self._normalize(raw_data, self.coordinator.external_normalizers.normalize_track(raw_data))
        else:
            return self._normalize(raw_data, self.coordinator.internal_normalizers.normalize_track(raw_data))
        
    def _normalize(self, raw_data: dict, source: RepoBundle) -> dict:
        return source.normalize.track(raw_data)

    def _get_one_from_norm_raw(self, norm_data: dict) -> Track:
        if not norm_data: # TODO: Is this necessary? We check if we have norm_data before calling others.
            return None
        
        track = self._get_or_cache(norm_data['id'], lambda: map_track(norm_data))

        if norm_data["album"]:  
            track.album = self.coordinator.album_service._get_one_from_norm_raw(norm_data["album"])

            if track not in track.album.tracks:
                track.album.tracks.append(track)

        if norm_data["artists"]:
            track.artists = self.coordinator.artist_service._get_many_from_norm_raw(norm_data["artists"])

        return track
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_track(self, track_id: str, prefer_external: bool=True) -> Track:
        return self.get_tracks([track_id], prefer_external=prefer_external)[0]
    
    def get_tracks(self, track_ids: list[str], prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.track.get_tracks(track_ids),
            prefer_external
        )
    
    def get_track_recommendations(self, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.track.get_track_recommendations(),
            prefer_external
        )
    
    def get_album_tracks(self, album_id: str, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.track.get_album_tracks(album_id),
            prefer_external
        )

    def get_playlist_tracks(self, playlist_id: str, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.track.get_playlist_tracks(playlist_id),
            prefer_external
        )