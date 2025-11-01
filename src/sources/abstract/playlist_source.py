from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractPlaylistSource(ABC):
    @abstractmethod
    def normalize(self, playlist: dict) -> dict:
        pass

    @abstractmethod
    def get_playlist(self, playlist_id: str) -> dict:
        pass

    @abstractmethod
    def get_playlists(self, playlist_ids: list[str]) -> list[dict]:
        pass
    
    @abstractmethod
    def add_tracks_to_playlist(self, track_ids: list[str], playlist_id: str) -> None:
        pass

    @abstractmethod
    def create_playlist(self, name: str, description: str='', public: bool=False) -> dict:
        pass

    @abstractmethod
    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None) -> dict:
        pass

    @abstractmethod
    def remove_playlist_tracks(self, playlist_id: str) -> None:
        pass