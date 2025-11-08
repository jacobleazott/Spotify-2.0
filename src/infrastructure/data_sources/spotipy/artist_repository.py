from domain import AbstractArtistRepository

from .proxy import SpotipyProxy

from src.common.utils import chunks

class SpotipyArtistRepository(AbstractArtistRepository):
    def __init__(self, spotipy_proxy: SpotipyProxy) -> None:
        self.sp = spotipy_proxy

    def get_artist(self, artist_id: str) -> dict:
        return self.sp.artist(artist_id, market="US")

    def get_artists(self, artist_ids: list[str]) -> list[dict]:
        artists = []

        for chunk in chunks(artist_ids, 50):
            response = self.sp.artists(chunk, market="US")
            artists.extend(response)

        return artists
    
    def get_related_artists(self, artist_id: dict) -> list[dict]:
        return self.sp.artist_related_artists(artist_id)

    # TODO
    def normalize(self, artist: dict) -> dict:
        pass