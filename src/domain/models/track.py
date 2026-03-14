from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .artist import Artist

if TYPE_CHECKING:
    from .album import Album

@dataclass
class Track:
    id: str
    name: str
    duration_ms: int
    is_local: bool
    is_playable: bool
    disc_number: int
    track_number: int
    album: Album | None = field(default=None, repr=False)
    artists: list[Artist] = field(default_factory=list, repr=False)
    
    def __str__(self) -> str:
        def indent(text: str, prefix: str = "\t") -> str:
            return '\n'.join(prefix + line for line in text.split('\n'))
        
        album_str = indent(str(self.album)) if self.album else "\tAlbum: None"
        artists_str = '\n'.join(indent(str(artist)) for artist in self.artists) if self.artists else "\tArtists: None"

        return (
            f"Track: {self.name}, id: {self.id}\n"
            f"\tduration: {self.duration_ms}\n"
            f"\tis_local: {self.is_local}\n"
            f"\tis_playable: {self.is_playable}\n"
            f"\tdisc_number: {self.disc_number}\n"
            f"\ttrack_number: {self.track_number}\n"
            f"{album_str}\n"
            f"{artists_str}"
        )

