from domain import AbstractAlbumRepository

from .proxy import SpotipyProxy

from src.common.utils import chunks

class SpotipyAlbumRepository(AbstractAlbumRepository):
    def __init__(self, spotipy_proxy: SpotipyProxy):
        self.sp = spotipy_proxy
        
    def get_album(self, album_id: str) -> dict:
        return self.sp.album(album_id, market="US")

    def get_albums(self, album_ids: list[str]) -> list[dict]:
        albums = []

        for chunk in chunks(album_ids, 20):
            response = self.sp.albums(chunk, market="US")
            albums.extend(response)

        return albums

    # TODO: Move Album Types to Enum, and then need an Enum-> spotify mapping
    def get_artist_albums(self, artist_id: str, album_types: list[str]=['album']) -> list[dict]:
        return self.sp.artist_albums(
            artist_id,
            country="US",
            limit=50,
            include_groups=','.join(album_types)
        )

    # TODO: 
    def normalize(self, album: dict) -> dict:
        pass