from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractPlaybackRepository(ABC):
    @abstractmethod
    def get_playback(self) -> dict:
        pass

    @abstractmethod
    def write_to_queue(self, track_ids: list[str]) -> None:
        pass

    @abstractmethod
    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        pass

    @abstractmethod
    def get_recent_tracks(self) -> list[dict]:
        pass

    @abstractmethod
    def normalize(self, playback_raw: dict) -> dict:
        pass