
from src.services import TrackService, AlbumService, ArtistService, PlaylistService, PlaybackService, UserService
from src.models import Track, Album, Artist, Playlist, Playback, User

class Coordinator():

    def __init__(self):
        self.track_service = TrackService()
        self.artist_service = ArtistService()
        self.album_service = AlbumService()
        self.playlist_service = PlaylistService()
        self.playback_service = PlaybackService()
        self.user_service = UserService()

    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        tracks = []
        tracks_data = self.track_service.get_tracks(track_ids)
        for track_data in tracks_data:
            track = self.track_service.map_track(track_data)
            track.album = self.album_service.map_album(track_data['album'])
            track.artists = [self.artist_service.map_artist(a) for a in track_data['artists']]
            tracks.append(track)

        return tracks
            
            
