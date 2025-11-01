from dataclasses import dataclass, field
from typing import Optional, Callable

from src.models.track import Track

@dataclass
class Playlist:
    id: str
    name: str
    description: str
    snapshot_id: str
    total_tracks: int
    tracks: list[Track] = field(default_factory=list, repr=False)

    def __str__(self) -> str:
        return f"id: {self.id}\n" + \
               f"name: {self.name}\n" + \
               f"\t description: {self.description}\n" + \
               f"\t snapshot_id: {self.snapshot_id}\n" + \
               f"\t total_tracks: {self.total_tracks}\n" + \
               f"\t tracks: {', '.join([track.id for track in self.tracks])}\n"