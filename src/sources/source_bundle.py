from src.common.enums import DataSource
from src.sources.abstract import TrackSource, ArtistSource, AlbumSource, PlaybackSource

class SourceBundle:
    def __init__(
        self,
        source_type: DataSource,
        track: Optional[TrackSource] = None,
        artist: Optional[ArtistSource] = None,
        album: Optional[AlbumSource] = None,
        playback: Optional[PlaybackSource] = None,
    ):
        self.source_type = source_type
        self.track = track or UnsupportedSource("track", source_type)
        self.artist = artist or UnsupportedSource("artist", source_type)
        self.album = album or UnsupportedSource("album", source_type)
        self.playback = playback or UnsupportedSource("playback", source_type)
