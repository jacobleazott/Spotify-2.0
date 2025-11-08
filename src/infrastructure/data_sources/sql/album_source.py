from domain import AbstractAlbumRepository

class SqlAlbumSource(AbstractAlbumRepository):
    def get_album(self, album_id: str) -> dict:
        pass

    def get_albums(self, album_ids: list[str]) -> list[dict]:
        pass

    def get_artist_albums(self, artist_id: str) -> list[dict]:
        pass