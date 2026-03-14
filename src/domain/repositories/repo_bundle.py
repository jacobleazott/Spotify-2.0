from abc import ABC, abstractmethod
from .album_repository import AbstractAlbumRepository
from .artist_repository import AbstractArtistRepository
from .playback_repository import AbstractPlaybackRepository
from .playlist_repository import AbstractPlaylistRepository
from .track_repository import AbstractTrackRepository
from .user_repository import AbstractUserRepository

from src.common.enums import DataSource

class RepoBundle:
    def __init__(
        self,
        source_type: DataSource,
        album: AbstractAlbumRepository | None = None,
        artist: AbstractArtistRepository | None = None,
        playback: AbstractPlaybackRepository | None = None,
        playlist: AbstractPlaylistRepository | None = None,
        track: AbstractTrackRepository | None = None,
        user: AbstractUserRepository | None = None,
    ):
        self.source_type = source_type
        self.album = album or UnsupportedSource("album", source_type)
        self.artist = artist or UnsupportedSource("artist", source_type)
        self.playback = playback or UnsupportedSource("playback", source_type)
        self.playlist = playlist or UnsupportedSource("playlist", source_type)
        self.track = track or UnsupportedSource("track", source_type)
        self.user = user or UnsupportedSource("user", source_type)

    def supports(self, domain: str) -> bool:
        repo = getattr(self, domain, None)
        return repo is not None and not isinstance(repo, UnsupportedSource)


class UnsupportedSource:
    def __init__(self, domain: str, source_type: DataSource):
        self._domain = domain
        self._source_type = source_type

    def __getattr__(self, attr):
        raise NotImplementedError(
            f"{self._source_type.value} source does not implement '{attr}' for domain '{self._domain}'."
        )

    def __repr__(self):
        return f"<UnsupportedSource domain={self._domain} source={self._source_type.value}>"