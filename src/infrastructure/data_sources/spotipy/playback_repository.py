from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractPlaybackRepository(ABC):
    def normalize(self, playback: dict) -> dict:
        pass

    def get_playback(self) -> dict:
        pass
    
    def write_to_queue(self, track_ids: list[str]) -> None:
        pass

    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        pass
    
    def get_recent_tracks(self) -> list[dict]:
        pass