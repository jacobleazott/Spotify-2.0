from src.sources import SourceBundle

from .identity_map import IdentityMap
from .album_service import AlbumService
from .artist_service import ArtistService
from .track_service import TrackService

class ServiceCoordinator:
    def __init__(self, external_source: SourceBundle, internal_source: SourceBundle):
        self.id_map = IdentityMap()
        self.ext_source = external_source
        self.int_source = internal_source

        self.track_service = None
        self.album_service = None
        self.artist_service = None

    def bind_services(self, track_service: TrackService, album_service: AlbumService, artist_service: ArtistService):
        self.track_service = track_service
        self.album_service = album_service
        self.artist_service = artist_service