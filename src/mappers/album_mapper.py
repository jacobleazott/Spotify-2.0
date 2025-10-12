from src.models.track import Track
from src.models.album import Album
from src.models.playlist import Playlist
from src.models.user import User
from src.models.artist import Artist

from src.common.enums import DataSource

def normalize_album_data(data: dict, src: DataSource) -> dict:
    match src:
        case DataSource.SPOTIPY:
            return normalize_album_data_from_spotipy(data)
        case DataSource.DB:
            return normalize_album_data_from_db(data)
        
def normalize_album_data_from_spotipy(data: dict) -> dict:

    if "albums" in data:
        for album in data["albums"]:
            normalized_album = []
            normalized_album["type"] = "album"
            normalized_album["id"] = album["id"]
            # etc...
            normalized_album["tracks"] = normalize_track_data_from_spotipy(album["tracks"])
            normalized_album["artists"] = normalize_artist_data_from_spotipy(album["artists"])

    # Important to normalize both the artist and track data as well

    # Under no key
    # Under ['albums']
    # Under ['items'] if get_artist_albums

    # Album artists always under ['artists']
    #   I think artists will always be populated
    # Tracks under ['tracks']['items']
    #    tracks might be under just ['items'] if request was get_album_tracks
    #    tracks might not be populated at all if get_artist_albums



    return data

def normalize_album_data_from_db(data: dict) -> dict:
    # Important to normalize both the artist and track data as well
    return data

##########################################################################################3
##########################################################################################3
##########################################################################################3

def map_album(data: dict, src: DataSource) -> Album:
    match src:
        case DataSource.SPOTIPY:
            return map_album_from_spotipy(data)
        case DataSource.DB:
            return map_album_from_db(data)

def map_album_from_spotipy(data: dict) -> Album:
    return Album(
        id=data['id'],
        name=data['name'],
        release_date=data['release_date'],
        total_albums=data['total_albums'],
    )

def map_album_from_db(data: dict) -> Album:
    return Album(
        id=data['id'],
        name=data['name'],
        release_date=data['release_date'],
        total_albums=data['total_albums'],
    )
