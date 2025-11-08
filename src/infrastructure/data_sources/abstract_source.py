from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# from src.models import Track, Album, Artist, Playlist, Playback, User

class OLDAbstractSource(ABC):
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACKS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
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

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ALBUMS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_album(self, album_id: str) -> dict:
        pass

    @abstractmethod
    def get_albums(self, album_ids: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_artist_albums(self, artist_id: str) -> list[dict]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ARTISTS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_artist(self, artist_id: str) -> dict:
        pass

    @abstractmethod
    def get_artists(self, artist_ids: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_related_artists(self, artist: dict) -> list[dict]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYLISTS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
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

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYBACK ════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def get_playback(self) -> dict:
        pass

    @abstractmethod
    def write_to_queue(self, tracks: list[dict]) -> None:
        pass

    @abstractmethod
    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        pass

    @abstractmethod
    def get_recent_tracks(self) -> list[dict]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # USER ════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def get_user_followed_artists(self, user: User) -> list[dict]:
        pass

    @abstractmethod
    def get_user_playlists(self, user: User) -> list[dict]:
        pass

    @abstractmethod
    def get_user_top_artists(self, user: User) -> list[dict]:
        pass

    @abstractmethod
    def get_user_top_tracks(self, user: User) -> list[dict]:
        pass

    @abstractmethod
    def get_user_queue(self, user: User) -> list[dict]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # NORMALIZERS ═════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def normalize_track(self, data: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def normalize_artist(self, data: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def normalize_album(self, data: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def normalize_playlist(self, data: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def normalize_user(self, data: Dict[str, Any]) -> dict:
        pass