from src.sources.abstract import SourceBundle

from .album_source import SpotifyAlbumSource
from .artist_source import SpotifyArtistSource
from .playback_source import SpotifyPlaybackSource
from .playlist_source import SpotifyPlaylistSource
from .track_source import SpotifyTrackSource
from .user_source import SpotifyUserSource

from src.common.enums import DataSource

class SpotipySource(SourceBundle):
    def __init__(self):
        super().__init__(
            source_type=DataSource.SPOTIPY,
            track=SpotifyAlbumSource(),
            album=SpotifyArtistSource(),
            artist=SpotifyPlaybackSource(),
            playlist=SpotifyPlaylistSource(),
            playback=SpotifyTrackSource(),
            user=SpotifyUserSource(),
            )