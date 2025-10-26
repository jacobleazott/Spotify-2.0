
from src.common.enums import DataSource
import logging
# from src.proxy.Spotipy_Proxy import SpotipyProxy
# from src.db.db_handler import DatabaseHandler
from src.services.artist_service import ArtistService
from src.services.album_service import AlbumService

from src.mappers.track_mapper import map_track, normalize_track_data
from src.mappers.artist_mapper import map_artist, normalize_artist_data
from src.mappers.album_mapper import map_album, normalize_album_data

from src.common.utils import chunks
import json
from pathlib import Path

from src.models import Track, Album, Artist
from src.sources.spotipy_source import SpotipyAPISource

class TrackService:
    def __init__(self) -> None:
        pass
        # , sp: SpotipyProxy,db: DatabaseHandler, artist_service: ArtistService, album_service: AlbumService
        # self.sp = sp
        # self.db = db
        # self.artist_service = artist_service
        # self.album_service = album_service


    def get_track(self, track_id: str, src: DataSource=DataSource.SPOTIPY):
        return self.get_tracks([track_id], src)[0]                          # Should we care about being efficient in one track get or just always use get_tracks
    
    def get_tracks(self, track_ids: list[str], src: DataSource) -> list[Track]:
        data_list = self.api_src.get_tracks(track_ids)
        
        tracks = [self.api_src.map_track(data) for data in data_list]

    def get_tracks(self, track_ids: list[str], src: DataSource=DataSource.SPOTIPY):
        data = None
        match src:
            case DataSource.SPOTIPY:
                for track_chunk in chunks(track_ids, 50):
                    data += self.sp.tracks(track_chunk, market="US")
            case DataSource.DB:
                placeholders = ",".join("?" for _ in track_ids)
                query = f"SELECT * FROM tracks WHERE id IN ({placeholders})"
                # data = self.db.execute_query(query, p_val=track_ids)
            case _:
                logging.error(f"Unknown data source: {src}")
                raise NotImplementedError(f"No implementation for data source: {src}")

        normalized_data = normalize_track_data(data, src)

        tracks = []
        for track_data in normalized_data:
            track = map_track(track_data, src)
            artists = [map_artist(artist, src) for artist in track_data['artists']]
            album = map_album(track_data['album'], src)
            track.artists = artists
            track.album = album
            tracks.append(track)

        return tracks
    
    def get_track_recommendations(self) -> list[Track]:
        data_list = self.api_src.get_track_recommendations()
        
        tracks = [self.api_src.map_track(data) for data in data_list]

        for track in tracks:
            track.album = self.api_src.map_album(self.api_src.normalizer_album(track['album']))
            track.artists = [self.api_src.map_artist(self.api_src.normalizer_artist(artist_data)) for artist_data in track['artists']]

        return tracks

    # def get_tracks(self, track_ids: list[str], src: DataSource=DataSource.SPOTIPY):
    #     data = None
    #     match src:
    #         case DataSource.SPOTIPY:
    #             for track_chunk in chunks(track_ids, 50):
    #                 data += self.sp.tracks(track_chunk, market="US")
    #         case DataSource.DB:
    #             placeholders = ",".join("?" for _ in track_ids)
    #             query = f"SELECT * FROM tracks WHERE id IN ({placeholders})"
    #             data = self.db.execute_query(query, p_val=track_ids)
    #         case _:
    #             logging.error(f"Unknown data source: {src}")
    #             raise NotImplementedError(f"No implementation for data source: {src}")

    #     normalized_data = normalize_track_data(data, src)

    #     tracks = []
    #     for track in normalized_data:
    #         track = map_track(track, src)
    #         artists = [map_artist(artist, src) for artist in track['artists']]
    #         album = map_album(track['album'], src)
    #         track.artists = artists
    #         track.album = album
    #         tracks.append(track)

    #     return tracks


    def get_track_artists(self):            # Probably not needed since it will be handled by ArtistService
        pass

    def verify_appears_on_tracks(self):     # Should probably be handled like a feature and then we add a search functionality
        pass


def process_get_track(data):
    src = DataSource.SPOTIPY
    
    normalized_data = normalize_track_data(data, src)

    tracks = []
    for track_data in normalized_data:
        track = map_track(track_data, src)
        artists = [map_artist(artist, src) for artist in track_data['artists']]
        album = map_album(track_data['album'], src)
        track._artists = artists
        track._album = album
        tracks.append(track)

    return tracks

def process_get_album_tracks(album_id, data):
    src = DataSource.SPOTIPY
    
    normalized_data = normalize_track_data(data, src)

    tracks = []
    for track_data in normalized_data:
        track = map_track(track_data, src)
        artists = [map_artist(artist, src) for artist in track_data['artists']]
        # album = map_album(track_data['album'], src)
        track._artists = artists
        track._album_id = album_id
        tracks.append(track)

    return tracks


def process_get_album(data):
    src = DataSource.SPOTIPY
    
    normalized_data = normalize_album_data(data, src)

    albums = []
    for album_data in normalized_data:
        album = map_album(album_data, src)
        artists = [map_artist(artist, src) for artist in album_data['artists']]
        tracks = [map_track(track, src) for track in album_data['tracks']]
        album._artists = artists
        album._tracks = tracks
        albums.append(album)

    return tracks


if __name__ == "__main__":
    current_dir = Path(__file__).parent

    # Build the path to data.json relative to this file

    ######### TRACK RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_several_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_track.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_recommendations.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_users_saved_tracks.json"

    ######### ALBUM RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/albums/get_album_tracks.json"
    data_path = current_dir / "../../tests/sample_responses/albums/get_album.json"
    # data_path = current_dir / "../../tests/sample_responses/albums/get_several_albums.json"

    ######### ARTIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artist.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_albums.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_related_artists.json"

    ######### PLAYLIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/playlists/create_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_current_users_playlists.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist_items.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_users_playlists.json"

    ######### USER RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/users/get_current_users_profile.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_followed_artists.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_profile.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_top_items_artists.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_top_items_tracks.json"

    ######### PLAYER RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/player/get_currently_playing_track.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_playback_state.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_recently_played_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_users_queue.json"

    # Load JSON safely
    with data_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # tracks = process_get_track(data)
    # tracks = process_get_album_tracks("my_album_id", data['albums'][0]['tracks'])
    tracks = process_get_album(data)
    
    for track in tracks:
        print(track)
        print(track.album)
        for artist in track.artists:
            print(artist)