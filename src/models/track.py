from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .album import Album
    from .artist import Artist

@dataclass
class Track:
    id: str
    name: str
    duration_ms: int
    is_local: bool
    is_playable: bool
    disc_number: int
    track_number: int
    album: Optional[Album] = field(default=None, repr=False)
    artists: list[Artist] = field(default_factory=list, repr=False)
    
    def __str__(self) -> str:
        return  f"id: {self.id}\n" + \
                f"name: {self.name}\n" + \
                f"\t duration: {self.duration_ms}\n" + \
                f"\t is_local: {self.is_local}\n" + \
                f"\t is_playable: {self.is_playable}\n" + \
                f"\t disc_number: {self.disc_number}\n" + \
                f"\t track_number: {self.track_number}\n" + \
                f"\t album: {self.album.id}\n" + \
                f"\t artists: {', '.join([artist.id for artist in self.artists])}\n"
