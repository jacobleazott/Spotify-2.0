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
        self.source_type = DataSource.SPOTIPY
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
            source_type = self.source_type,
            album = self.album,
            artist = self.artist,
            playback = self.playback,
            playlist = self.playlist,
            track = self.track,
            user = self.user,
        )

# Next Claude Question
# I kind of like that "supports(...)" method but that just kind of kicks the can down the rode to the service right? Like I plan to have my Services support multiple different sources. That was kind of the idea of making them abstract to start, the services don't care where the data is coming from. They just "try" and get it. I guess the MusicApp would know because it knows which sources it is supporting but it doesn't know what the downstream users are using. It just is a facade to all the services. I guess it moves the failure one more level up? I don't think type checking will know it's bad because it won't necessarily know which sources I am currently using. Taking that into consideration is it worth doing all that extra supports business?