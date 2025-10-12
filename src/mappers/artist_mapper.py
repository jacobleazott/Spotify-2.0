from src.models.track import Track
from src.models.album import Album
from src.models.playlist import Playlist
from src.models.user import User
from src.models.artist import Artist
from src.common.enums import DataSource

def normalize_artist_data(data: dict, src: DataSource) -> dict:
    match src:
        case DataSource.SPOTIPY:
            return normalize_artist_data_from_spotipy(data)
        case DataSource.DB:
            return normalize_artist_data_from_db(data)
        
def normalize_artist_data_from_spotipy(data: dict) -> dict:
    # Under no key
    # Under ['artists']
    return data

def normalize_artist_data_from_db(data: dict) -> dict:
    return data

##########################################################################################3
##########################################################################################3
##########################################################################################3

def map_artist(data: dict, src: DataSource) -> Artist:
    match src:
        case DataSource.SPOTIPY:
            return map_artist_from_spotipy(data)
        case DataSource.DB:
            return map_artist_from_db(data)

def map_artist_from_spotipy(data: dict) -> Artist:
    return Artist(
        id=data['id'],
        name=data['name'],
    )

def map_artist_from_db(data: dict) -> Artist:
    return Artist(
        id=data['id'],
        name=data['name'],
    )
