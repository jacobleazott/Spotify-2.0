from src.models.track import Track
from src.models.album import Album
from src.models.playlist import Playlist
from src.models.user import User
from src.models.artist import Artist
from src.common.enums import DataSource

from src.mappers.album_mapper import normalize_album_data
from src.mappers.artist_mapper import normalize_artist_data

def normalize_track_data(data: dict, src: DataSource) -> dict:
    match src:
        case DataSource.SPOTIPY:
            return normalize_track_data_from_spotipy(data)
        case DataSource.DB:
            return normalize_track_data_from_db(data)
        

# List under ['tracks']
# Under no key
# List under ['items']['tracks']
# if grabbing from get_album ['tracks']['items']
# if grabbing from currently_playing under ['item']
# if grabbing from get_recently_played under ['items']['track']
# if grabbing by get_queue under ['currently_playing'] or list under ['queue']
# If getting from get_user_playlists it might just contain an href under ['items']['tracks']
# If getting from get_playlist_items list under ['items']
# Sometimes need to check if ['type'] == 'track'


# album always under ['album']
#   album can be not present if get_album_tracks

# artists always under ['artists']
# NOTE ONLY WHEN FETCHING TRACKS DIRECTLY, ALBUMS AND PLAYLISTS MAY ACT DIFFERENTLY
def normalize_track_data_from_spotipy(data: dict) -> dict:
    # Important to normalize both the artist and album data as well
    tracks = []
    track_items = []

    if "tracks" in data:
        if "items" in data["tracks"]:               # get_several_albums, get_playlist
            track_items = data["tracks"]["items"]
        else:                                       # get_several_tracks
            track_items = data["tracks"]
    elif "items" in data:
        if "track" in data["items"][0]:             # get_recently_played_tracks
            for item in data["items"]:
                track_items.append(item["track"])
        else:                                       # get_album_tracks, get_playlist_items
            track_items = data["items"]
    elif "item" in data:                            # get_currently_playing
        track_items = [data["item"]]
    else:
        if type(data) is list:                      # get_users_queue ['queue']
            track_items = data
        else:                                       # get_track
            track_items = [data]
    
    # Check if id is present                        # get_user_playlists
    for item in track_items:
        if item.get("type", None) == "track":
            item["artists"] = normalize_artist_data(item["artists"], src=DataSource.SPOTIPY)
            item["album"] = normalize_album_data(item["album"], src=DataSource.SPOTIPY)
            tracks.append(item)
        
    return tracks

def normalize_track_data_from_db(data: dict) -> dict:
    # Important to normalize both the artist and album data as well
    return data

##########################################################################################3
##########################################################################################3
##########################################################################################3

def map_track(data: dict, src: DataSource) -> Track:
    match src:
        case DataSource.SPOTIPY:
            return map_track_from_spotipy(data)
        case DataSource.DB:
            return map_track_from_db(data)

def map_track_from_spotipy(data: dict) -> Track:
    return Track(
        id           = data['id'],
        name         = data['name'],
        duration_ms  = data['duration_ms'],
        is_local     = data['is_local'],
        is_playable  = data['preview_url'] is not None,
        disc_number  = data['disc_number'],
        track_number = data['track_number'],
        album_id     = data.get('album', {}).get('id', None),       # OPTIONAL
        artist_ids   = [artist['id'] for artist in data['artists']],
    )

def map_track_from_db(data: dict) -> Track:
    return Track(
    )


# def get_artist(artist_id: str, src: str) -> Artist:
#     if src == 'api':
#         return from_api(get_artist_data(artist_id))
#     elif src == 'db':
#         return from_db(get_artist_data(artist_id))
    

# def get_track(track_id: str, src: str) -> Track:
#     data = None
#     if src == 'api':
#         data = sp.get_track(track_id)
#     elif src == 'db':
#         data = db.query("SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()

#     normalized_data = normalize_track_data(data, src)
    
#     track = map_track(normalized_data, src)
#     artists = [map_artist(artist, src) for artist in normalized_data['artists']]
#     album = map_album(normalized_data, src)

#     track.artists = artists
#     track.album = album

#     return track

# # Can think about having a "universal" cache or having individual caches for each object type
# def check_artist_cache(artists: list[Artist]) -> list[Artist]:
#     result = []
#     for artist in artists:
#         if artist.id in artist_cache:
#             result.append(artist_cache[artist.id])
#         else:
#             artist_cache[artist.id] = artist
#             result.append(artist)
#     return result


# def map_track(data: dict, src: str) -> Track:
#     if src == 'api':
#         return Track(
#             id=data['id'],
#             name=data['name'],
#             duration_ms=data['duration_ms'],
#             is_local=data['is_local'],
#             is_playable=data['is_playable'],
#             disc_number=data['disc_number'],
#             track_number=data['track_number'],
#             album_id=data['album']['id'],
#             artist_ids=[artist['id'] for artist in data['artists']],
#         )
#     elif src == 'db':
#         return Track(
#             id=data['id'],
#             name=data['name'],
#             duration_ms=data['duration_ms'],
#             is_local=data['is_local'],
#             is_playable=data['is_playable'],
#             disc_number=data['disc_number'],
#             track_number=data['track_number'],
#             album_id=data['album_id'],
#             artist_ids=data['artist_ids'],
#         )
    

