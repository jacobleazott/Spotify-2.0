from src.services.coordinator import Coordinator
from src.models import Album
from src.mappers import map_album
from src.sources.abstract_source import AbstractSource
from src.services.base_service import BaseService

class AlbumService(BaseService[Album]):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(Album, coordinator)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # BASE METHODS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        return source.normalize_album(raw_data)
    
    def get_one_from_norm_raw(self, norm_data: dict) -> Album:    
        if not norm_data:
            return None
        
        album = self.get_or_cache(norm_data['id'], lambda: map_album(norm_data))

        if norm_data["tracks"]:
            album.tracks = self.coordinator.track_service.get_many_from_norm_raw(norm_data["tracks"])
            # TODO: Do I need to go through each track and populate the album id, obj ref?

        if norm_data["artists"]:
            album.artists = self.coordinator.artist_service.get_many_from_norm_raw(norm_data["artists"])

        return album
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_album(self, album_id: str, prefer_external: bool=True) -> Album:
        return self.get_albums([album_id], prefer_external=prefer_external)[0]

    def get_albums(self, album_ids: list[str], prefer_external: bool=True) -> list[Album]:
        return self._fetch_and_hydrate(
            lambda s: s.get_albums(album_ids),
            prefer_external
        )

    def get_artist_albums(self, artist_id: str, prefer_external: bool=True) -> list[Album]:
        return self._fetch_and_hydrate(
            lambda s: s.get_artist_albums(artist_id),
            prefer_external
        )
    

