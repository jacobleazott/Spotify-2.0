from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .track import Track
    from .artist import Artist

@dataclass
class Album:
    id: str
    name: str
    release_date: str
    album_type: str
    total_tracks: int
    track_ids: list[str] = field(default_factory=list)
    artist_ids: list[str] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list, repr=False)
    artist: Optional[Artist] = field(default=None, repr=False)
    
    def __str__(self) -> str:
        return f"id: {self.id}\n" + \
               f"name: {self.name}\n" + \
               f"\trelease_date: {self.release_date}\n" + \
               f"\talbum_type: {self.album_type}\n" + \
               f"\ttotal_tracks: {self.total_tracks}\n" + \
               f"\tracks: {', '.join([id for id in self.track_ids])}\n" + \
               f"\artists: {', '.join([id for id in self.artist_ids])}\n"
