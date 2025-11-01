from src.models import Playlist

def map_playlist(playlist_data: dict) -> Playlist:
    return Playlist(
        id           = playlist_data['id'],
        name         = playlist_data['name'],
        description  = playlist_data['description'],
        snapshot_id  = playlist_data['snapshot_id'],
        total_tracks = playlist_data['total_tracks'],
    )
