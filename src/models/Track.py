from dataclasses import dataclass, field
from typing import Optional, List, Callable
from Artist import Artist
from Album import Album

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
    _artist_ids: List[str]

    _album: Optional["Album"] = field(default=None, init=False, repr=False)
    _artists: Optional[List["Artist"]] = field(default=None, init=False, repr=False)

    _album_loader: Optional[Callable[[str], "Album"]] = field(default=None, repr=False)
    _artist_loader: Optional[Callable[[List[str]], List["Artist"]]] = field(default=None, repr=False)

    @property
    def album(self) -> Optional["Album"]:
        if self._album is None and self._album_loader:
            self._album = self._album_loader(self._album_id)
        return self._album

    @property
    def artists(self) -> List["Artist"]:
        if self._artists is None and self._artist_loader:
            self._artists = self._artist_loader(self._artist_ids)
        return self._artists
