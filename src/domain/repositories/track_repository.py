from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractTrackRepository(ABC):
    @abstractmethod
    def get_track(self, track_id: str) -> dict:
        pass
    
    @abstractmethod
    def get_tracks(self, track_ids: list[str]) -> list[dict]:
        pass
    
    @abstractmethod
    def get_track_recommendations(self) -> list[dict]:
        pass
    
    @abstractmethod
    def get_playlist_tracks(self, playlist_id: str, offset: int) -> list[dict]:
        pass
