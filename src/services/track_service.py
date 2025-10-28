from src.services.coordinator import Coordinator
from src.models import Track
from src.mappers import map_track
from src.sources.abstract_source import AbstractSource

class TrackService:
    def __init__(self, coordinator: Coordinator) -> None:
        self.coordinator = coordinator
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    def extract_unique_albums_and_artists(self, tracks_data: list[dict]) -> tuple[dict[str, dict], dict[str, dict]]:
        unique_albums: dict[str, dict] = {}
        unique_artists: dict[str, dict] = {}

        for track in tracks_data:
            # Albums
            album_raw = track.get("album")
            if album_raw and (a_id := album_raw.get("id")):
                if a_id not in unique_albums:
                    unique_albums[a_id] = album_raw

                # Artists on the Album
                for artist_raw in album_raw.get("artists", []):
                    if artist_raw and (ar_id := artist_raw.get("id")) and ar_id not in unique_artists:
                        unique_artists[ar_id] = artist_raw

            # Artists on the Track
            for artist_raw in track.get("artists", []):
                if artist_raw and (ar_id := artist_raw.get("id")) and ar_id not in unique_artists:
                    unique_artists[ar_id] = artist_raw

        return unique_albums, unique_artists

    def _get_track_from_norm_raw(self, track_data: dict, source: AbstractSource) -> Track:
        if cached := self.coordinator.id_map.get(Track, track_data['id']):
            return cached

        track = map_track(track_data)
        self.coordinator.id_map.set(Track, track.id, track)

        album = self.coordinator.album_service.get_album_from_raw(track_data['album'], source)
        artists = [self.coordinator.artist_service.get_artists_from_raw(track_data['artists'], source)]

        track.artists = artists
        track.album = album

        album.track_ids.append(track.id)
        album.tracks.append(track)

        return track
    
    def get_tracks_from_raw(self, tracks_data: list[dict], source: AbstractSource) -> list[Track]:
        # Need to decide if we want to handle normalzing one or batches in the abstract source?
        norm_tracks_data = source.normalize_track(tracks_data)                                      
        unique_albums, unique_artists = self.extract_unique_albums_and_artists(norm_tracks_data)

        for artist_raw in unique_artists.values():
            self.coordinator.artist_service.get_artist_from_raw(artist_raw, source)

        for album_raw in unique_albums.values():
            self.coordinator.album_service.get_album_from_raw(album_raw, source)

        return [self._get_track_from_norm_raw(track_raw, source) for track_raw in norm_tracks_data]
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════    
    def get_track(self, track_id: str, prefer_external: bool=True) -> Track:
        return self.get_tracks([track_id], prefer_external=prefer_external)[0]
    
    def get_tracks(self, track_ids: list[str], prefer_external: bool=True) -> list[Track]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_tracks_from_raw(source.get_tracks(track_ids), source)
    
    def get_track_recommendations(self, prefer_external: bool=True) -> list[Track]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_tracks_from_raw(source.get_track_recommendations(), source)
    
    def get_album_tracks(self, album_id: str, prefer_external: bool=True) -> list[Track]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_tracks_from_raw(source.get_album_tracks(album_id), source)

    def get_playlist_tracks(self, playlist_id: str, prefer_external: bool=True) -> list[Track]:
        source = self.coordinator.ext_source if prefer_external else self.coordinator.int_source
        return self.get_tracks_from_raw(source.get_playlist_tracks(playlist_id), source)