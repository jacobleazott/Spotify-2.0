from src.sources.abstract import SourceBundle

from .album_source import SqlAlbumSource
from .artist_source import SqlArtistSource
# from .playback_source import SqlPlaybackSource
from .playlist_source import SqlPlaylistSource
from .track_source import SqlTrackSource
# from .user_source import SqlUserSource

from src.common.enums import DataSource

class SqlSource(SourceBundle):
    def __init__(self):
        super().__init__(
            source_type=DataSource.SQL,
            track=SqlTrackSource(),
            album=SqlAlbumSource(),
            artist=SqlArtistSource(),
            playlist=SqlPlaylistSource(),
            # playback=SqlPlaybackSource(), # Not implemented
            # user=SqlUserSource(),         # Not implemented
            )