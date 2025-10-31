from src.services.coordinator import Coordinator
from src.models import Track
from src.mappers import map_track
from src.sources.abstract_source import AbstractSource
from src.services.base_service import BaseService

class TrackService(BaseService[Track]):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(Track, coordinator)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        return source.normalize_track(raw_data)

    def get_one_from_norm_raw(self, norm_data: dict) -> Track:
        if not norm_data:
            return None
        
        track = self.get_or_cache(norm_data['id'], lambda: map_track(norm_data))

        if norm_data["album"]:  
            track.album = self.coordinator.album_service.get_one_from_norm_raw(norm_data["album"])
            if track.id not in track.album.track_ids:
                track.album.track_ids.append(track.id)

            if track not in track.album.tracks:
                track.album.tracks.append(track)

        if norm_data["artists"]:
            track.artists = self.coordinator.artist_service.get_many_from_norm_raw(norm_data["artists"])

        return track
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_track(self, track_id: str, prefer_external: bool=True) -> Track:
        return self.get_tracks([track_id], prefer_external=prefer_external)[0]
    
    def get_tracks(self, track_ids: list[str], prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.get_tracks(track_ids),
            prefer_external
        )
    
    def get_track_recommendations(self, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.get_track_recommendations(),
            prefer_external
        )
    
    def get_album_tracks(self, album_id: str, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.get_album_tracks(album_id),
            prefer_external
        )

    def get_playlist_tracks(self, playlist_id: str, prefer_external: bool=True) -> list[Track]:
        return self._fetch_and_hydrate(
            lambda s: s.get_playlist_tracks(playlist_id),
            prefer_external
        )