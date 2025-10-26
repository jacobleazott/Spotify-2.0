from __future__ import annotations

from dataclasses import dataclass, field
<<<<<<< Updated upstream
from typing import Optional, Callable
=======
from typing import Optional, List, Callable

# from src.models.track import Track
# from src.models.artist import Artist


>>>>>>> Stashed changes

@dataclass
class Album:
    id: str
    name: str
    release_date: str
    album_type: str
    total_tracks: int
<<<<<<< Updated upstream
    tracks: list["Track"]
    artists: list["Artist"]
=======
>>>>>>> Stashed changes

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
    
    def __str__(self) -> str:
        return f"id: {self.id}\n" + \
               f"name: {self.name}\n" + \
               f"release_date: {self.release_date}\n" + \
               f"album_type: {self.album_type}\n" + \
               f"total_tracks: {self.total_tracks}\n"
