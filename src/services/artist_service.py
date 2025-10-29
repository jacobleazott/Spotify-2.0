from src.services.coordinator import Coordinator
from src.models import Artist
from src.mappers import map_artist
from src.sources.abstract_source import AbstractSource
from src.services.base_service import BaseService

class ArtistService(BaseService):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(Artist, coordinator)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _get_from_norm_raw(self, norm_data: dict, source: AbstractSource) -> Artist:
        return self.get_or_cache(norm_data['id'], lambda: map_artist(norm_data))
    
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        return source.normalize_artist(raw_data)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_artist(self, artist_id: str, prefer_external: bool=True):
        return self.get_artists([artist_id], prefer_external=prefer_external)[0]

    def get_artists(self, artist_ids: list[str], prefer_external: bool=True):
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_many_from_raw(source.get_artists(artist_ids), source)
    
    def get_related_artists(self, artist_id: str, prefer_external: bool=True):
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_many_from_raw(source.get_related_artists(artist_id), source)