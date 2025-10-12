from dataclasses import dataclass, field
from typing import Optional, List, Callable
from Track import Track
from Playlist import Playlist
from Artist import Artist

@dataclass
class User:
    username: str
    description: str
    email: str

    _playlists: Optional[List["Playlist"]] = field(default=None, init=False, repr=False)
    _following: Optional[List["Artist"]] = field(default=None, init=False, repr=False)

    _playlist_loader: Optional[Callable[[List[str]], List["Playlist"]]] = field(default=None, repr=False)
    _following_loader: Optional[Callable[[List[str]], List["Artist"]]] = field(default=None, repr=False)

    @property
    def playlists(self) -> List["Playlist"]:
        if self._playlists is None and self._playlist_loader:
            self._playlists = self._playlist_loader(self._playlists)
        return self._playlists
    
    @property
    def following(self) -> List["Artist"]:
        if self._following is None and self._following_loader:
            self._following = self._following_loader(self._following)
        return self._following