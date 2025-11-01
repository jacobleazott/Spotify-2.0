from src.sources.abstract_source import AbstractSource
from typing import Any, Dict, List, Optional

from src.models import Track, Album, Artist, Playlist, Playback, User
from src.proxy.Spotipy_Proxy import SpotipyProxy


class SpotipyAPISource(AbstractSource):
    def __init__(self):
        self.sp = SpotipyProxy()

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACKS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def get_track(self, track_id: str) -> Track:
        pass

    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        pass
    
    def get_track_recommendations(self) -> list[Track]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ALBUMS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_album(self, album_id: str) -> Album:
        pass

    def get_albums(self, album_ids: list[str]) -> list[Album]:
        pass
    
    def get_album_tracks(self, album_id: str) -> list[Track]:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ARTISTS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_artist(self, artist_id: str) -> Artist:
        pass

    def get_artists(self, artist_ids: list[str]) -> list[Artist]:
        pass
    
    def get_artist_albums(self, artist_id: str) -> list[Album]:
        pass
    
    def get_related_artists(self, artist: Artist) -> list[Artist]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYLISTS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    def get_playlist(self, playlist_id: str) -> Playlist:
        pass

    def get_playlists(self, playlist_ids: list[str]) -> list[Playlist]:
        pass
    
    def add_tracks_to_playlist(self, track_ids: list[str], playlist_id: str) -> None:
        pass

    def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        pass
    
    def create_playlist(self, name, description: str='', public: bool=False) -> Playlist:
        pass

    def change_playlist_details(self, playlist_id: str, name: Optional[str]=None, description: Optional[str]=None) -> Playlist:
        pass

    def remove_playlist_tracks(self, playlist_id: str) -> None:
        pass

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYBACK ════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def get_playback(self) -> Playback:
        pass
    
    def write_to_queue(self, tracks: list[Track]) -> None:
        pass

    def change_playback(self, pause: Optional[bool]=None, skip: str="", shuffle: Optional[bool]=None, repeat: str="") -> None:
        pass

    def get_recent_tracks(self) -> list[Track]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # USER ════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def get_user_followed_artists(self, user: User) -> list[Artist]:
        pass

    def get_user_playlists(self, user: User) -> list[Playlist]:
        pass

    def get_user_top_artists(self, user: User) -> list[Artist]:
        pass
    
    def get_user_top_tracks(self, user: User) -> list[Track]:
        pass

    def get_user_queue(self, user: User) -> list[Track]:
        pass
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MAPPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def map_track(self, data: Dict[str, Any]) -> Track:
        return Track(
            id           = data['id'],
            name         = data['name'],
            duration_ms  = data['duration_ms'],
            is_local     = data['is_local'],
            is_playable  = data['preview_url'] is not None,
            disc_number  = data.get('disc_number', -1),
            track_number = data.get('track_number', -1),
            album_id     = data.get('album', {}).get('id', None),       # OPTIONAL
            artist_ids   = [artist['id'] for artist in data['artists']],
        )

    def map_artist(self, data: Dict[str, Any]) -> Artist:
        return Artist(
            id   = data['id'],
            name = data['name'],
        )

    def map_album(self, data: Dict[str, Any]) -> Album:
        return Album(
            id           = data['id'],
            name         = data['name'],
            release_date = data['release_date'],
            album_type   = data['album_type'],
            total_tracks = data['total_tracks'],
        )

    def map_playlist(self, data: Dict[str, Any]) -> Playlist:
        return Playlist(
            id          = data['id'],
            name        = data['name'],
            description = data['description'],
        )

    def map_user(self, data: Dict[str, Any]) -> User:
        pass


    def get_track(self, track_id: str) -> Dict[str, Any]:
        data = self.client.track(track_id)
        return self._normalize_track(data)

    def get_tracks(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        response = self.client.tracks(track_ids)
        return [self._normalize_track(t) for t in response['tracks']]

    def get_album(self, album_id: str) -> Dict[str, Any]:
        data = self.client.album(album_id)
        return self._normalize_album(data)

    def get_albums(self, album_ids: List[str]) -> List[Dict[str, Any]]:
        response = self.client.albums(album_ids)
        return [self._normalize_album(a) for a in response['albums']]

    def get_artist(self, artist_id: str) -> Dict[str, Any]:
        data = self.client.artist(artist_id)
        return self._normalize_artist(data)

    def get_artists(self, artist_ids: List[str]) -> List[Dict[str, Any]]:
        response = self.client.artists(artist_ids)
        return [self._normalize_artist(a) for a in response['artists']]

    # --- Private Normalizers (specific to this source) ---
    def _normalize_track(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data["id"],
            "name": data["name"],
            "album": data["album"],  # full album object (can be parsed by album_service)
            "artists": data["artists"],  # list of artist dicts
            "duration_ms": data["duration_ms"],
        }

    def _normalize_album(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data["id"],
            "name": data["name"],
            "artists": data["artists"],
            "release_date": data.get("release_date"),
        }

    def _normalize_artist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data["id"],
            "name": data["name"],
            "genres": data.get("genres", []),
        }
