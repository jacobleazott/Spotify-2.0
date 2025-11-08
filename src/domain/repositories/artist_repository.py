from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractArtistRepository(ABC):
    @abstractmethod
    def get_artist(self, artist_id: str) -> dict:
        pass

    @abstractmethod
    def get_artists(self, artist_ids: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_related_artists(self, artist_id: dict) -> list[dict]:
        pass

    @abstractmethod
    def normalize(self, artist_raw: dict) -> dict:
        pass