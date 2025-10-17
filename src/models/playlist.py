from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class Playlist:
    id: str
    name: str
    description: str
    tracks: list["Track"]

    _track_ids: list[str]
    _tracks: Optional[list["Track"]] = field(default=None, init=False, repr=False)
    _track_loader: Optional[Callable[[list[str]], list["Track"]]] = field(default=None, repr=False)

    @property
    def tracks(self) -> list["Track"]:
        if self._tracks is None and self._track_loader:
            self._album = self._track_loader(self._track_ids)
        return self._tracks