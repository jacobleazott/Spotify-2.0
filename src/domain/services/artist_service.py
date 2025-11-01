from src.models import Artist
from src.mappers import map_artist
from src.sources import SourceBundle

from .service_coordinator import ServiceCoordinator
from .base_service import BaseService

class ArtistService(BaseService[Artist]):
    def __init__(self, coordinator: ServiceCoordinator) -> None:
        super().__init__(Artist, coordinator)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _normalize(self, raw_data: dict, source: SourceBundle) -> dict:
        return source.artist.normalize(raw_data)
    
    def _get_one_from_norm_raw(self, norm_data: dict) -> Artist:
        if not norm_data:
            return None
        
        return self._get_or_cache(norm_data['id'], lambda: map_artist(norm_data))
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_artist(self, artist_id: str, prefer_external: bool=True) -> Artist:
        return self.get_artists([artist_id], prefer_external=prefer_external)[0]

    def get_artists(self, artist_ids: list[str], prefer_external: bool=True) -> list[Artist]:
        return self._fetch_and_hydrate(
            lambda s: s.artist.get_artists(artist_ids),
            prefer_external
        )
    
    def get_related_artists(self, artist_id: str, prefer_external: bool=True) -> list[Artist]:
        return self._fetch_and_hydrate(
            lambda s: s.artist.get_related_artists(artist_id),
            prefer_external
        )