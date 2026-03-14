from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.models import Album

class AbstractAlbumRepository(ABC):
    @abstractmethod
    def get_album(self, album_id: str) -> Album:
        pass

    @abstractmethod
    def get_albums(self, album_ids: list[str]) -> list[Album]:
        pass

    @abstractmethod
    def get_artist_albums(self, artist_id: str) -> list[Album]:
        pass