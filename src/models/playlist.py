from dataclasses import dataclass, field
from typing import Optional, List, Callable
from track import Track

@dataclass
class Playlist:
    id: str
    name: str
    description: str
    tracks: list[Track]

    _track_ids: List[str]
    _tracks: Optional[List["Track"]] = field(default=None, init=False, repr=False)
    _track_loader: Optional[Callable[[List[str]], List["Track"]]] = field(default=None, repr=False)

    @property
    def tracks(self) -> List["Track"]:
        if self._tracks is None and self._track_loader:
            self._album = self._track_loader(self._track_ids)
        return self._tracks