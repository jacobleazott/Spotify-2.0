from abc import ABC, abstractmethod
from .album_repository import SpotipyAlbumRepository
from .artist_repository import SpotipyArtistRepository
from .playback_repository import SpotipyPlaybackRepository
from .playlist_repository import SpotipyPlaylistRepository
from .track_repository import SpotipyTrackRepository
from .user_repository import SpotipyUserRepository

from .proxy import SpotipyProxy

from src.common.enums import DataSource

from domain import RepoBundle


class SpotipyRepositoryBundle(RepoBundle):
    def __init__(self):
        self.sp = SpotipyProxy()

        # Instantiate Repositories In Order Of Dependency
        self.artist = SpotipyArtistRepository(self.sp)
        self.user = SpotipyUserRepository(self.sp)

        self.track = SpotipyTrackRepository(self.sp, self.artist)

        self.album = SpotipyAlbumRepository(self.sp, self.track)
        self.playback = SpotipyPlaybackRepository(self.sp, self.track)
        self.playlist = SpotipyPlaylistRepository(self.sp, self.track)

        # Bind Any Necessary Repositories
        self.track.bind_album_repository(self.album)

        super().__init__(
            source_type = DataSource.SPOTIPY,
            album = self.album,
            artist = self.artist,
            playback = self.playback,
            playlist = self.playlist,
            track = self.track,
            user = self.user,
        )
