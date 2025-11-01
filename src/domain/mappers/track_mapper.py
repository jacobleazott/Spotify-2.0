from src.models import Track

def map_track(track_data: dict) -> Track:
    return Track(
        id           = track_data['id'],
        name         = track_data['name'],
        duration_ms  = track_data['duration_ms'],
        is_local     = track_data['is_local'],
        is_playable  = track_data['preview_url'] is not None,
        disc_number  = track_data['disc_number'],
        track_number = track_data['track_number'],
    )
