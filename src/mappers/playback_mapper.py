from src.models import Playback

def map_playback(playback_data: dict) -> Playback:
    return Playback(
        device_id      = playback_data['device']['id'],
        device_name    = playback_data['device']['name'],
        volume_percent = playback_data['device']['volume_percent'],
        progress_ms    = playback_data['progress_ms'],
        is_playing     = playback_data['is_playing'],
        shuffle        = playback_data['shuffle_state'],
        repeat         = playback_data['repeat_state'],
        timestamp      = playback_data['timestamp'],
    )
