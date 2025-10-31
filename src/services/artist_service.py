from src.services.coordinator import Coordinator
from src.models import Artist
from src.mappers import map_artist
from src.sources.abstract_source import AbstractSource
from src.services.base_service import BaseService

class ArtistService(BaseService[Artist]):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(Artist, coordinator)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        return source.normalize_artist(raw_data)
    
    def get_one_from_norm_raw(self, norm_data: dict) -> Artist:
        if not norm_data:
            return None
        
        return self.get_or_cache(norm_data['id'], lambda: map_artist(norm_data))
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_artist(self, artist_id: str, prefer_external: bool=True) -> Artist:
        return self.get_artists([artist_id], prefer_external=prefer_external)[0]

    def get_artists(self, artist_ids: list[str], prefer_external: bool=True) -> list[Artist]:
        return self._fetch_and_hydrate(
            lambda s: s.get_artists(artist_ids),
            prefer_external
        )
    
    def get_related_artists(self, artist_id: str, prefer_external: bool=True) -> list[Artist]:
        return self._fetch_and_hydrate(
            lambda s: s.get_related_artists(artist_id),
            prefer_external
        )