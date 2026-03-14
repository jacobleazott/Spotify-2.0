from domain import Album, AbstractAlbumRepository

from .artist_repository import SpotipyArtistRepository
from .track_repository import SpotipyTrackRepository
from .proxy import SpotipyProxy

from src.common.utils import chunks


class SpotipyAlbumRepository(AbstractAlbumRepository):
    
    def __init__(self, spotipy_proxy: SpotipyProxy, 
                 artist_repository: SpotipyArtistRepository,
                 track_repository: SpotipyTrackRepository) -> None:
        self.sp = spotipy_proxy
        self.artist = artist_repository
        self.track = track_repository
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_album(self, album_id: str) -> Album:
        raw = self.sp.album(album_id, market="US")
        return self.build_album(raw)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_albums(self, album_ids: list[str]) -> list[Album]:
        albums = []

        for album_chunk in chunks(album_ids, 20):
            response = self.sp.albums(album_chunk, market="US")
            for raw in response['albums']:
                albums.append(self.build_album(raw))

        return albums

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # TODO: Move Album Types to Enum, and then need an Enum-> spotify mapping
    def get_artist_albums(self, artist_id: str, album_types: list[str]=['album']) -> list[Album]:
        albums = []

        response = self.sp.artist_albums(
            artist_id,
            country="US",
            limit=50,
            include_groups=','.join(album_types)
        )

        for raw in response['items']:
            albums.append(self.build_album(raw))

        # TODO: Handle Pagination Probably Dynamically For All of Spotify
        while response['next']:
            response = self.sp.next(response)
            for raw in response['items']:
                albums.append(self.build_album(raw))

        return albums

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def build(self, album_raw: dict) -> Album:
        if not album_raw or not album_raw.get("id"):
            return None

        tracks = [self.track.build(artist) for artist in (album_raw.get("tracks", {}).get("items", []))]
        artists = [self.artist.build(artist) for artist in (album_raw.get("artists", []))]

        return Album(
            id=album_raw["id"],
            name=album_raw.get("name", ""),
            release_date=album_raw.get("release_date", ""),
            album_type=album_raw.get("album_type", ""),
            total_tracks=album_raw.get("total_tracks", 0),
            tracks=tracks,
            artists=artists,
        )