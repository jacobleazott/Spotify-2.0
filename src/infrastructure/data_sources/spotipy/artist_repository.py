from domain import Artist, AbstractArtistRepository

from .proxy import SpotipyProxy

from src.common.utils import chunks

class SpotipyArtistRepository(AbstractArtistRepository):
    def __init__(self, spotipy_proxy: SpotipyProxy) -> None:
        self.sp = spotipy_proxy

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_artist(self, artist_id: str) -> Artist:
        raw = self.sp.artist(artist_id, market="US")
        return self.build(raw)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_artists(self, artist_ids: list[str]) -> list[Artist]:
        artists = []

        for artist_chunk in chunks(artist_ids, 50):
            response = self.sp.artists(artist_chunk, market="US")
            for raw in response['artists']:
                artists.append(self.build(raw))

        return artists

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def get_related_artists(self, artist_id: dict) -> list[Artist]:
        artists = []

        response = self.sp.artist(artist_id, market="US")

        for raw in response['artists']:
            artists.append(self.build(raw))

        return artists

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def build(self, artist_raw: dict) -> Artist:
        if not artist_raw or not artist_raw.get("id"):
            return None
        
        return Artist(
            id=artist_raw["id"],
            name=artist_raw.get("name", ""),
        )