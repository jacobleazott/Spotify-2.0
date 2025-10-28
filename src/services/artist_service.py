from src.services.coordinator import Coordinator
from src.models import Artist
from src.mappers import map_artist
from src.sources.abstract_source import AbstractSource

class ArtistService:
    def __init__(self, coordinator: Coordinator) -> None:
        self.coordinator = coordinator

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _get_artist_from_norm_raw(self, artist_data: dict) -> Artist:
        if cached := self.coordinator.id_map.get(Artist, artist_data['id']):
            return cached
        
        artist = map_artist(artist_data)
        self.coordinator.id_map.set(Artist, artist.id, artist)

        return artist
    
    def get_artists_from_raw(self, artists_data: list[dict], source: AbstractSource) -> list[Artist]:
        norm_artist_data = source.normalize_artist(artists_data)
        return [self._get_artist_from_norm_raw(track_raw) for track_raw in norm_artist_data]
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_artist(self, artist_id: str, prefer_external: bool=True):
        return self.get_artists([artist_id], prefer_external=prefer_external)[0]

    def get_artists(self, artist_ids: list[str], prefer_external: bool=True):
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_artists_from_raw(source.get_artists(artist_ids), source)
    
    def get_related_artists(self, artist_id: str, prefer_external: bool=True):
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_artists_from_raw(source.get_related_artists(artist_id), source)