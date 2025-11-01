from src.models import Album
from src.mappers import map_album
from src.sources import abstract_source
from src.sources import SourceBundle

from .service_coordinator import ServiceCoordinator
from .base_service import BaseService

class AlbumService(BaseService[Album]):
    def __init__(self, coordinator: ServiceCoordinator) -> None:
        super().__init__(Album, coordinator)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _normalize(self, raw_data: dict, source: SourceBundle) -> dict:
        return source.album.normalize(raw_data)
    
    def _get_one_from_norm_raw(self, norm_data: dict) -> Album:    
        if not norm_data:
            return None
        
        album = self._get_or_cache(norm_data['id'], lambda: map_album(norm_data))

        if norm_data["tracks"]:
            album.tracks = self.coordinator.track_service._get_many_from_norm_raw(norm_data["tracks"])
            # TODO: Do I need to go through each track and populate the album id, obj ref?

        if norm_data["artists"]:
            album.artists = self.coordinator.artist_service._get_many_from_norm_raw(norm_data["artists"])

        return album
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_album(self, album_id: str, prefer_external: bool=True) -> Album:
        return self.get_albums([album_id], prefer_external=prefer_external)[0]

    def get_albums(self, album_ids: list[str], prefer_external: bool=True) -> list[Album]:
        return self._fetch_and_hydrate(
            lambda s: s.album.get_albums(album_ids),
            prefer_external
        )

    def get_artist_albums(self, artist_id: str, prefer_external: bool=True) -> list[Album]:
        return self._fetch_and_hydrate(
            lambda s: s.album.get_artist_albums(artist_id),
            prefer_external
        )
    

