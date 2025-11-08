
from domain.services import (
    TrackService,
    ArtistService,
    AlbumService,
    PlaylistService,
    PlaybackService,
    UserService
)
from domain.core import IdentityMap, ServiceCoordinator
from domain.repositories import RepoBundle
from common.enums import DataSource

def generate_source(source_type: DataSource):
    match source_type:
        case DataSource.SPOTIPY:
            from infrastructure.data_sources.spotipy import SpotipyRepositoryBundle
            return SpotipyRepositoryBundle()
        case DataSource.DB:
            from infrastructure.data_sources.sql.sql_source import SqlSource
            return SqlSource()
        case _:
            raise NotImplementedError

class MusicApp():
    def __init__(self, external_source: DataSource, internal_source: DataSource):
        external_source, external_normalizers = generate_source(external_source)
        internal_source, internal_normalizers = generate_source(internal_source)

        self._id_map = IdentityMap()
        self._coordinator = ServiceCoordinator(self._id_map, external_source, internal_source, external_normalizers, internal_normalizers)

        self.track    = TrackService(self._coordinator)
        self.artist   = ArtistService(self._coordinator)
        self.album    = AlbumService(self._coordinator)
        self.playlist = PlaylistService(self._coordinator)
        self.playback = PlaybackService(self._coordinator)
        self.user     = UserService(self._coordinator)
        
        self._coordinator.bind_services(self.track, self.album, self.artist)
