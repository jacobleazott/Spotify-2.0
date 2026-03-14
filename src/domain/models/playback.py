from dataclasses import dataclass, field

from .track import Track

@dataclass
class Playback:
    playlist_id: str
    device_id: str
    device_name: str
    volume_percent: int
    progress_ms: int
    is_playing: bool
    shuffle: str
    smart_shuffle: bool
    repeat: str
    timestamp: int
    track: Track | None = field(default=None, repr=False)

    def __str__(self) -> str:
        return f"Track.id: {self.track.id if self.track else 'None'}\n" + \
               f"Track.name: {self.track.name if self.track else 'None'}\n" + \
               f"\t Playlist ID: {self.playlist_id}\n" + \
               f"\t Device ID: {self.device_id}\n" + \
               f"\t Device Name: {self.device_name}\n" + \
               f"\t Volume: {self.volume_percent}\n" + \
               f"\t Progress: {self.progress_ms}\n" + \
               f"\t Is Playing: {self.is_playing}\n" + \
               f"\t Shuffle: {self.shuffle}\n" + \
               f"\t Repeat: {self.repeat}\n" + \
               f"\t Timestamp: {self.timestamp}\n"