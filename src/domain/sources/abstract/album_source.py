from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractAlbumSource(ABC):
    @abstractmethod
    def normalize(self, album: dict) -> dict:
        pass
    
    @abstractmethod
    def get_album(self, album_id: str) -> dict:
        pass

    @abstractmethod
    def get_albums(self, album_ids: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_artist_albums(self, artist_id: str) -> list[dict]:
        pass