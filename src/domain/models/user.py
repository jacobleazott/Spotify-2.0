from dataclasses import dataclass, field

from .playlist import Playlist
from .artist import Artist

@dataclass
class User:
    username: str
    id: str
    email: str
    country: str
    playlists: list[Playlist] = field(default_factory=list)
    followed_artists: list[Artist] = field(default_factory=list)

    def __str__(self) -> str:
        return f"username: {self.username}\n" + \
               f"\t id: {self.id}\n" + \
               f"\t email: {self.email}\n" + \
               f"\t country: {self.country}\n" + \
               f"\t playlists: {', '.join([playlist.id for playlist in self.playlists])}\n" + \
               f"\t followed_artists: {', '.join([artist.id for artist in self.followed_artists])}\n"