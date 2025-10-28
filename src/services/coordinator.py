from src.services.identity_map import IdentityMap
from src.sources.abstract_source import AbstractSource

class Coordinator:
    def __init__(self, external_source: AbstractSource, internal_source: AbstractSource):
        self.id_map = IdentityMap()
        self.ext_source = external_source
        self.int_source = internal_source

        self.track_service = None
        self.album_service = None
        self.artist_service = None

    def bind_services(self, track_service, album_service, artist_service):
        self.track_service = track_service
        self.album_service = album_service
        self.artist_service = artist_service