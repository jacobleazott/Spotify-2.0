from src.models import Album

def map_album(album_data: dict) -> Album:
    return Album(
        id           = album_data['id'],
        name         = album_data['name'],
        release_date = album_data['release_date'],
        album_type   = album_data['album_type'],
        total_tracks = album_data['total_tracks'],
        track_ids    = [t['id'] for t in album_data.get('tracks', [])],     # OPTIONAL
        artist_ids   = [ar['id'] for ar in album_data.get('artists', [])],  # OPTIONAL
    )