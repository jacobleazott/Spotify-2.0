from dataclasses import dataclass, field
from typing import Optional, Callable

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
