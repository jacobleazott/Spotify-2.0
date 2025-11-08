from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.models import User

class AbstractUserRepository(ABC):
    def normalize(self, user: dict) -> dict:
        pass

    def get_user_followed_artists(self, user: User) -> list[dict]:
        pass

    def get_user_playlists(self, user: User) -> list[dict]:
        pass

    def get_user_top_artists(self, user: User) -> list[dict]:
        pass
    
    def get_user_top_tracks(self, user: User) -> list[dict]:
        pass
    
    def get_user_queue(self, user: User) -> list[dict]:
        pass