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
    repeat: str
    timestamp: int
    track: Track | None = field(default=None, repr=False)

    def __str__(self) -> str:
        return f"Track.id: {self.track.id if self.track else 'None'}" + \
               f"Track.name: {self.track.name if self.track else 'None'}" + \
               f"\t Playlist ID: {self.playlist_id}" + \
               f"\t Device ID: {self.device_id}" + \
               f"\t Device Name: {self.device_name}" + \
               f"\t Volume: {self.volume_percent}" + \
               f"\t Progress: {self.progress_ms}" + \
               f"\t Is Playing: {self.is_playing}" + \
               f"\t Shuffle: {self.shuffle}" + \
               f"\t Repeat: {self.repeat}" + \
               f"\t Timestamp: {self.timestamp}"
