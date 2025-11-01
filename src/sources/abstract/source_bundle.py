from abc import ABC, abstractmethod
from .album_source import AbstractAlbumSource
from .artist_source import AbstractArtistSource
from .playback_source import AbstractPlaybackSource
from .playlist_source import AbstractPlaylistSource
from .track_source import AbstractTrackSource
from .user_source import AbstractUserSource
from typing import Any, Dict, List, Optional

from src.common.enums import DataSource

class SourceBundle:
    def __init__(
        self,
        source_type: DataSource,
        album: AbstractAlbumSource | None = None,
        artist: AbstractArtistSource | None = None,
        playback: AbstractPlaybackSource | None = None,
        playlist: AbstractPlaylistSource | None = None,
        track: AbstractTrackSource | None = None,
        user: AbstractUserSource | None = None,
    ):
        self.source_type = source_type
        self.album = album or UnsupportedSource("album", source_type)
        self.artist = artist or UnsupportedSource("artist", source_type)
        self.playback = playback or UnsupportedSource("playback", source_type)
        self.playlist = playlist or UnsupportedSource("playlist", source_type)
        self.track = track or UnsupportedSource("track", source_type)
        self.user = user or UnsupportedSource("user", source_type)


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