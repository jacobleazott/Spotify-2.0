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

    album_id: Optional[str] = None
    artist_ids: list[str] = field(default_factory=list)
    album: Optional[Album] = field(default=None, repr=False)
    artists: list[Artist] = field(default_factory=list, repr=False)
    
    def __str__(self) -> str:
        return  f"id: {self.id}\n" + \
                f"name: {self.name}\n" + \
                f"\tduration: {self.duration_ms}\n" + \
                f"\tis_local: {self.is_local}\n" + \
                f"\tis_playable: {self.is_playable}\n" + \
                f"\tdisc_number: {self.disc_number}\n" + \
                f"\ttrack_number: {self.track_number}\n" + \
                f"\talbum: {self.album_id}\n" + \
                f"\tartists: {', '.join([id for id in self.artist_ids])}\n"
