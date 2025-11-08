from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractPlaylistRepository(ABC):
    def normalize(self, playlist: dict) -> dict:
        pass

    def get_playlist(self, playlist_id: str) -> dict:
        pass

    def get_playlists(self, playlist_ids: list[str]) -> list[dict]:
        pass

    def add_tracks_to_playlist(self, track_ids: list[str], playlist_id: str) -> None:
        pass

    def create_playlist(self, name: str, description: str='', public: bool=False) -> dict:
        pass

    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None) -> dict:
        pass

    def remove_playlist_tracks(self, playlist_id: str) -> None:
        pass
    