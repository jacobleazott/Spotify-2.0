from domain.repositories import RepoBundle
from domain.services import AlbumService, ArtistService, TrackService

from .identity_map import IdentityMap

# TODO: Maybe call this DomainContext?
class ServiceCoordinator:
    def __init__(self, id_map: IdentityMap, external_source: RepoBundle, internal_source: RepoBundle):
        self.id_map = id_map
        self.ext_source = external_source
        self.int_source = internal_source

        self.track_service = None
        self.album_service = None
        self.artist_service = None

    def bind_services(self, track_service: TrackService, album_service: AlbumService, artist_service: ArtistService):
        self.track_service = track_service
        self.album_service = album_service
        self.artist_service = artist_service