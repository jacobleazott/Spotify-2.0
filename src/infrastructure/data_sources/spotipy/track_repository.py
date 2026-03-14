from domain import AbstractTrackRepository, AbstractArtistRepository, AbstractAlbumRepository
from domain import Track

from .proxy import SpotipyProxy

from src.common.utils import chunks

class SpotipyTrackRepository(AbstractTrackRepository):
    def __init__(self, spotipy_proxy: SpotipyProxy, artist_repository: AbstractArtistRepository) -> None:
        self.sp = spotipy_proxy
        self.artist = artist_repository

        self.album = None

    def bind_album_repository(self, album_repository: AbstractAlbumRepository):
        self.album = album_repository

    def get_track(self, track_id: str) -> Track:
        raw = self.sp.track(track_id, market="US")
        return self.build_track(raw)

    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        tracks = []

        for chunk in chunks(track_ids, 50):
            response = self.sp.tracks(chunk, market="US")
            for raw in response['tracks']:
                tracks.append(self.build_track(raw))
        
        return tracks

    # TODO: Is this going to be the 'recommendations' through spotipy? or something diff from the artist one
    def get_track_recommendations(self) -> list[Track]:
        raise NotImplementedError
    
    def get_playlist_tracks(self, playlist_id: str, offset: int=0) -> list[Track]:
        results = self.sp.playlist_items(playlist_id, limit=100, offset=offset, market="US")
        tracks = []

        def process_items(items):
            for item in items:
                if item and item.get('track'):
                    tracks.append(self.build_track(item['track']))

        process_items(results['items'])

        while results['next']:
            results = self.sp.next(results)
            process_items(results['items'])

        return tracks
    
    def build_track(self, track_raw: dict) -> Track:
        if not track_raw:
            return None
        
        if 'track' in track_raw:
            track_raw = track_raw['track']
        if 'item' in track_raw:
            track_raw = track_raw['item']
        
        if not track_raw or not track_raw.get('id'):
            return None
        
        album = self.album.build_album(track_raw.get("album"))
        artists = [self.artist.build_album(artist) for artist in (track_raw.get("artists"))]

        return Track(
            id=track_raw["id"],
            name=track_raw.get("name", ""),
            duration_ms=track_raw.get("duration_ms", 0),
            is_local=track_raw.get("is_local", False),
            preview_url=track_raw.get("preview_url"),
            disc_number=track_raw.get("disc_number", 1),
            track_number=track_raw.get("track_number", 0),
            album=album,
            artists=artists
        )