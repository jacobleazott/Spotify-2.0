from dataclasses import dataclass, field
from typing import Optional, List, Callable
from Track import Track
from Artist import Artist

@dataclass
class Album:
    id: str
    name: str
    release_date: str
    album_type: str
    total_tracks: int
    tracks: list[Track]
    artists: list[Artist]

    _track_ids: List[str]
    _artist_ids: List[str]

    _tracks: Optional[List["Track"]] = field(default=None, init=False, repr=False)
    _artists: Optional[List["Artist"]] = field(default=None, init=False, repr=False)

    _track_loader: Optional[Callable[[List[str]], List["Track"]]] = field(default=None, repr=False)
    _artist_loader: Optional[Callable[[List[str]], List["Artist"]]] = field(default=None, repr=False)

    @property
    def tracks(self) -> List["Track"]:
        if self._tracks is None and self._track_loader:
            self._album = self._track_loader(self._track_ids)
        return self._tracks

    @property
    def artists(self) -> List["Artist"]:
        if self._artists is None and self._artist_loader:
            self._artists = self._artist_loader(self._artist_ids)
        return self._artists
