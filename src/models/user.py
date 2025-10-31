from dataclasses import dataclass, field
from typing import Optional, Callable
from .playlist import Playlist
from .artist import Artist

@dataclass
class User:
    username: str
    description: str
    email: str
    playlists: list[Playlist] = field(default_factory=list)
    followed_artists: list[Artist] = field(default_factory=list)

    def __str__(self) -> str:
        return f"username: {self.username}\n" + \
               f"\t description: {self.description}\n" + \
               f"\t email: {self.email}\n" + \
               f"\t playlists: {', '.join([playlist.id for playlist in self.playlists])}\n" + \
               f"\t followed_artists: {', '.join([artist.id for artist in self.followed_artists])}\n"