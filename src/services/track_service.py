
from src.common.enums import DataSource
import logging
from src.proxy.Spotipy_Proxy import SpotipyProxy
from src.db.db_handler import DatabaseHandler
from src.services.artist_service import ArtistService
from src.services.album_service import AlbumService

from src.mappers.track_mapper import map_track, normalize_track_data
from src.mappers.artist_mapper import map_artist
from src.mappers.album_mapper import map_album

from src.common.utils import chunks

class TrackService:
    def __init__(self, sp: SpotipyProxy, db: DatabaseHandler, artist_service: ArtistService, album_service: AlbumService) -> None:
        self.sp = sp
        self.db = db
        self.artist_service = artist_service
        self.album_service = album_service


    def get_track(self, track_id: str, src: DataSource=DataSource.SPOTIPY):
        return self.get_tracks([track_id], src)[0]

    def get_tracks(self, track_ids: list[str], src: DataSource=DataSource.SPOTIPY):
        data = None
        match src:
            case DataSource.SPOTIPY:
                for track_chunk in chunks(track_ids, 50):
                    data += self.sp.tracks(track_chunk, market="US")
            case DataSource.DB:
                placeholders = ",".join("?" for _ in track_ids)
                query = f"SELECT * FROM tracks WHERE id IN ({placeholders})"
                data = self.db.execute_query(query, p_val=track_ids)
            case _:
                logging.error(f"Unknown data source: {src}")
                raise NotImplementedError(f"No implementation for data source: {src}")

        normalized_data = normalize_track_data(data, src)

        tracks = []
        for track in normalized_data:
            track = map_track(track, src)
            artists = [map_artist(artist, src) for artist in track['artists']]
            album = map_album(track['album'], src)
            track.artists = artists
            track.album = album
            tracks.append(track)

        return tracks


    def get_track_artists(self):            # Probably not needed since it will be handled by ArtistService
        pass

    def verify_appears_on_tracks(self):     # Should probably be handled like a feature and then we add a search functionality
        pass