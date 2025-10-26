from src.models.track import Track
from src.models.album import Album
# from src.models.playlist import Playlist
# from src.models.user import User
from src.models.artist import Artist


from src.mappers import normalize_artist_data, normalize_track_data

from src.common.enums import DataSource

def normalize_album_data(data: dict, src: DataSource) -> dict:
    match src:
        case DataSource.SPOTIPY:
            return normalize_album_data_from_spotipy(data)
        case DataSource.DB:
            return normalize_album_data_from_db(data)


# Important to normalize both the artist and track data as well

# Under no key
# Under ['albums']
# Under ['items'] if get_artist_albums

# Album artists always under ['artists']
#   I think artists will always be populated
# Tracks under ['tracks']['items']
#    tracks might be under just ['items'] if request was get_album_tracks
#    tracks might not be populated at all if get_artist_albums
def normalize_album_data_from_spotipy(data: dict) -> dict:
    albums = []
    album_items = []

    if "albums" in data:
        if "items" in data["albums"]:               # get_several_albums, get_playlist
            album_items = data["albums"]["items"]
        else:                                       # get_several_tracks
            album_items = data["albums"]
    elif "items" in data:
        if "album" in data["items"][0]:             # get_recently_played_tracks
            for item in data["items"]:
                album_items.append(item["album"])
        else:                                       # get_album_tracks, get_playlist_items
            album_items = data["items"]
    elif "item" in data:                            # get_currently_playing
        album_items = [data["item"]]
    else:
        if type(data) is list:                      # get_users_queue ['queue']
            album_items = data
        else:                                       # get_track
            album_items = [data]
    
    # Check if id is present                        # get_user_playlists
    for item in album_items:
        item["artists"] = normalize_artist_data(item["artists"], src=DataSource.SPOTIPY)
        item["tracks"] = normalize_track_data(item["tracks"], src=DataSource.SPOTIPY)
        albums.append(item)

    return albums

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
        id            = data['id'],
        name          = data['name'],
        release_date  = data['release_date'],
        album_type    = data['album_type'],
        total_tracks  = data['total_tracks'],
        _track_ids    = [t['id'] for t in data.get('tracks', {})],
        _artist_ids   = [a['id'] for a in data.get('artists', {})],
    )

def map_album_from_db(data: dict) -> Album:
    return Album(
        id=data['id'],
        name=data['name'],
        release_date=data['release_date'],
    )
