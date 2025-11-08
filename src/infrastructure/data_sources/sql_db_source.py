from domain_source import AbstractSource

class SqlDbSource(AbstractSource):
    def __init__(self, client):
        self.client = client

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
