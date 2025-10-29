from src.services.coordinator import Coordinator
from src.models import Playlist
from src.mappers import map_playlist
from src.sources.abstract_source import AbstractSource
from src.services.base_service import BaseService

class PlaylistService(BaseService[Playlist]):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__(Playlist, coordinator)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def _get_from_norm_raw(self, norm_data: dict, source: AbstractSource) -> Playlist:
        playlist = self.get_or_cache(norm_data['id'], lambda: map_playlist(norm_data))

        tracks = self.coordinator.track_service.get_tracks_from_raw(norm_data['tracks'], source)
        playlist.tracks = tracks
        playlist.track_ids = [track.id for track in tracks]
        
        return playlist
    
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        return source.normalize_playlist(raw_data)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def get_playlist(self, playlist_id: str, prefer_external: bool=True) -> Playlist:
        return self.get_playlists([playlist_id], prefer_external=prefer_external)[0]
        
    def get_playlists(self, playlist_ids: list[str], prefer_external: bool=True) -> list[Playlist]:
        source = self.get_source(prefer_external)
        return self.get_many_from_raw(source.get_playlists(playlist_ids), source)

    # TODO: Should we maybe try to get the updated snapshot_id????
    # TODO: Does prefer_external make sense here?
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str], prefer_external: bool=True) -> None:
        source = self.get_source(prefer_external)
        return source.add_tracks_to_playlist(playlist_id, track_ids)
    
    def get_playlist_tracks(self):
        pass

    def create_playlist(self):
        pass

    def change_playlist_details(self):
        pass

    def remove_all_playlist_tracks(self):
        pass


