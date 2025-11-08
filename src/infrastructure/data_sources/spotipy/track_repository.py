from domain import AbstractTrackRepository

from .proxy import SpotipyProxy

from src.common.utils import chunks

class SpotipyTrackRepository(AbstractTrackRepository):
    def __init__(self, spotipy_proxy: SpotipyProxy):
        self.sp = spotipy_proxy

    def get_track(self, track_id: str) -> dict:
        return self.sp.track(track_id, market="US")

    def get_tracks(self, track_ids: list[str]) -> list[dict]:
        tracks = []

        for chunk in chunks(track_ids, 50):
            response = self.sp.tracks(chunk, market="US")
            tracks.extend(response)
        
        return tracks

    # TODO: Is this going to be the 'recommendations' through spotipy? or something diff from the artist one
    def get_track_recommendations(self) -> list[dict]:
        raise NotImplementedError
    
    def get_playlist_tracks(self, playlist_id: str, offset: int=0) -> list[dict]:
        results = self.sp.playlist_items(playlist_id, limit=100, offset=offset, market="US")
        tracks = results['items']

        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])

        return tracks
    