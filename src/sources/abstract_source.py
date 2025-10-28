from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.models import Track, Album, Artist, Playlist, Playback, User

class AbstractSource(ABC):
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACKS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_track(self, track_id: str) -> Track:
        pass

    @abstractmethod
    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        pass

    @abstractmethod
    def get_track_recommendations(self) -> list[Track]:
        pass

    @abstractmethod
    def get_album_tracks(self, album_id: str) -> list[Track]:
        pass

    @abstractmethod
    def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ALBUMS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_album(self, album_id: str) -> Album:
        pass

    @abstractmethod
    def get_albums(self, album_ids: list[str]) -> list[Album]:
        pass

    @abstractmethod
    def get_artist_albums(self, artist_id: str) -> list[Album]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ARTISTS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_artist(self, artist_id: str) -> Artist:
        pass

    @abstractmethod
    def get_artists(self, artist_ids: list[str]) -> list[Artist]:
        pass

    @abstractmethod
    def get_related_artists(self, artist: Artist) -> list[Artist]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYLISTS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def get_playlist(self, playlist_id: str) -> Playlist:
        pass

    @abstractmethod
    def get_playlists(self, playlist_ids: list[str]) -> list[Playlist]:
        pass
    
    @abstractmethod
    def add_tracks_to_playlist(self, track_ids: list[str], playlist_id: str) -> None:
        pass

    @abstractmethod
    def create_playlist(self, name, description: str='', public: bool=False) -> Playlist:
        pass

    @abstractmethod
    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None) -> Playlist:
        pass

    @abstractmethod
    def remove_playlist_tracks(self, playlist_id: str) -> None:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYBACK ════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def get_playback(self) -> Playback:
        pass

    @abstractmethod
    def write_to_queue(self, tracks: list[Track]) -> None:
        pass

    @abstractmethod
    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        pass

    @abstractmethod
    def get_recent_tracks(self) -> list[Track]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # USER ════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def get_user_followed_artists(self, user: User) -> list[Artist]:
        pass

    @abstractmethod
    def get_user_playlists(self, user: User) -> list[Playlist]:
        pass

    @abstractmethod
    def get_user_top_artists(self, user: User) -> list[Artist]:
        pass

    @abstractmethod
    def get_user_top_tracks(self, user: User) -> list[Track]:
        pass

    @abstractmethod
    def get_user_queue(self, user: User) -> list[Track]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # NORMALIZERS ═════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def normalize_track(self, data: Dict[str, Any]) -> Track:
        pass

    @abstractmethod
    def normalize_artist(self, data: Dict[str, Any]) -> Artist:
        pass

    @abstractmethod
    def normalize_album(self, data: Dict[str, Any]) -> Album:
        pass

    @abstractmethod
    def normalize_playlist(self, data: Dict[str, Any]) -> Playlist:
        pass

    @abstractmethod
    def normalize_user(self, data: Dict[str, Any]) -> User:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MAPPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    @abstractmethod
    def map_track(self, data: Dict[str, Any]) -> Track:
        pass

    @abstractmethod
    def map_artist(self, data: Dict[str, Any]) -> Artist:
        pass

    @abstractmethod
    def map_album(self, data: Dict[str, Any]) -> Album:
        pass

    @abstractmethod
    def map_playlist(self, data: Dict[str, Any]) -> Playlist:
        pass

    @abstractmethod
    def map_user(self, data: Dict[str, Any]) -> User:
        pass