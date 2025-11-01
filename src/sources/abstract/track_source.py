from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractTrackSource(ABC):
    @abstractmethod
    def normalize(self, track: dict) -> dict:
        pass

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
    def get_album_tracks(self, album_id: str) -> list[dict]:
        pass
    
    @abstractmethod
    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        pass