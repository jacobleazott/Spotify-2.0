
from src.services import TrackService, AlbumService, ArtistService, PlaylistService, PlaybackService, UserService, IdentityMap, ServiceCoordinator
from src.models import Track, Album, Artist, Playlist, Playback, User

class MusicApp():
    def __init__(self):
        self.id_map = IdentityMap()
        self.track_service = TrackService()
        self.artist_service = ArtistService()
        self.album_service = AlbumService()
        self.playlist_service = PlaylistService()
        self.playback_service = PlaybackService()
        self.user_service = UserService()
