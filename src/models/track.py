from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Callable
# from src.models.artist import Artist
# from src.models.album import Album

@dataclass
class Track:
    id: str
    name: str
    duration_ms: int
    is_local: bool
    is_playable: bool
    disc_number: int
    track_number: int

    _album_id: str
    _artist_ids: list[str]

    _album: Optional["Album"] = field(default=None, init=False, repr=False)
    _artists: Optional[list["Artist"]] = field(default=None, init=False, repr=False)

    _album_loader: Optional[Callable[[str], "Album"]] = field(default=None, repr=False)
    _artist_loader: Optional[Callable[[list[str]], list["Artist"]]] = field(default=None, repr=False)

    @property
    def album(self) -> Optional["Album"]:
        if self._album is None and self._album_loader:
            self._album = self._album_loader(self._album_id)
        return self._album

    @property
    def artists(self) -> list["Artist"]:
        if self._artists is None and self._artist_loader:
            self._artists = self._artist_loader(self._artist_ids)
        return self._artists
    
    def __str__(self) -> str:
        return  f"id: {self.id}\n" + \
                f"name: {self.name}\n" + \
                f"duration: {self.duration_ms}\n" + \
                f"is_local: {self.is_local}\n" + \
                f"is_playable: {self.is_playable}\n" + \
                f"disc_number: {self.disc_number}\n" + \
                f"track_number: {self.track_number}\n" + \
                f"album: {self._album_id}\n" + \
                f"artists: {', '.join([id for id in self._artist_ids])}\n"