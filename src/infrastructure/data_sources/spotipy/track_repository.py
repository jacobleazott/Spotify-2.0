from domain import Track, AbstractTrackRepository

from .album_repository import SpotipyAlbumRepository
from .artist_repository import SpotipyArtistRepository
from .proxy import SpotipyProxy

from src.common.utils import chunks


class SpotipyTrackRepository(AbstractTrackRepository):
    
    def __init__(self, spotipy_proxy: SpotipyProxy, artist_repository: SpotipyArtistRepository) -> None:
        self.sp = spotipy_proxy
        self.artist = artist_repository

        self.album = None

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def bind_album_repository(self, album_repository: SpotipyAlbumRepository):
        self.album = album_repository

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_track(self, track_id: str) -> Track:
        raw = self.sp.track(track_id, market="US")
        return self.build(raw)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        tracks = []

        for track_chunk in chunks(track_ids, 50):
            response = self.sp.tracks(track_chunk, market="US")
            for raw in response['tracks']:
                tracks.append(self.build(raw))
        
        return tracks

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # TODO: Is this going to be the 'recommendations' through spotipy? or something diff from the artist one
    def get_track_recommendations(self) -> list[Track]:
        raise NotImplementedError
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_playlist_tracks(self, playlist_id: str, offset: int=0) -> list[Track]:
        tracks = []
        response = self.sp.playlist_items(playlist_id, limit=100, offset=offset, market="US")

        def process_items(items):
            for item in items:
                if item and item.get('track'):
                    tracks.append(self.build(item['track']))

        process_items(response['items'])

        while response['next']:
            response = self.sp.next(response)
            process_items(response['items'])

        return tracks

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def build(self, track_raw: dict) -> Track:
        if not track_raw:
            return None
        
        if 'track' in track_raw:
            track_raw = track_raw['track']
        if 'item' in track_raw:
            track_raw = track_raw['item']
        
        if not track_raw or not track_raw.get('id'):
            return None
        
        album = self.album.build(track_raw.get("album"))
        artists = [self.artist.build(artist) for artist in (track_raw.get("artists"))]

        return Track(
            id=track_raw["id"],
            name=track_raw.get("name"),
            duration_ms=track_raw.get("duration_ms", 0),
            is_local=track_raw.get("is_local", False),
            is_playable=(track_raw.get("preview_url") is not None),
            disc_number=track_raw.get("disc_number", 0),
            track_number=track_raw.get("track_number", 0),
            album=album,
            artists=artists,
        )
    
