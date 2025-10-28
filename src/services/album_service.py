from src.services.coordinator import Coordinator
from src.models import Album
from src.mappers import map_album
from src.sources.abstract_source import AbstractSource

class AlbumService:
    def __init__(self, coordinator: Coordinator) -> None:
        self.coordinator = coordinator

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _get_album_from_norm_raw(self, album_data: dict) -> Album:
        if cached := self.coordinator.id_map.get(Album, album_data['id']):
            return cached

        album = map_album(album_data)
        self.coordinator.id_map.set(Album, album.id, album)

        return album
    
    def get_albums_from_raw(self, artists_data: list[dict], source: AbstractSource) -> list[Album]:
        norm_artist_data = source.normalize_artist(artists_data)
        return [self._get_artist_from_norm_raw(track_raw) for track_raw in norm_artist_data]
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_album(self, album_id: str, prefer_external: bool=True) -> Album:
        return self.get_albums([album_id], prefer_external=prefer_external)[0]

    def get_albums(self, album_ids: list[str], prefer_external: bool=True) -> list[Album]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_albums_from_raw(source.get_albums(album_ids), source)

    def get_artist_albums(self, artist_id: str, prefer_external: bool=True) -> list[Album]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_albums_from_raw(source.get_artist_albums(artist_id), source)
    

