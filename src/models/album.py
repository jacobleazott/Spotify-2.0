from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class Album:
    id: str
    name: str
    release_date: str
    album_type: str
    total_tracks: int
    tracks: list["Track"]
    artists: list["Artist"]

    _track_ids: list[str]
    _artist_ids: list[str]

    _tracks: Optional[list["Track"]] = field(default=None, init=False, repr=False)
    _artists: Optional[list["Artist"]] = field(default=None, init=False, repr=False)

    _track_loader: Optional[Callable[[list[str]], list["Track"]]] = field(default=None, repr=False)
    _artist_loader: Optional[Callable[[list[str]], list["Artist"]]] = field(default=None, repr=False)

    @property
    def tracks(self) -> list["Track"]:
        if self._tracks is None and self._track_loader:
            self._album = self._track_loader(self._track_ids)
        return self._tracks

    @property
    def artists(self) -> list["Artist"]:
        if self._artists is None and self._artist_loader:
            self._artists = self._artist_loader(self._artist_ids)
        return self._artists
