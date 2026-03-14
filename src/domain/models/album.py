from dataclasses import dataclass, field

from .artist import Artist
from .track import Track
    
@dataclass
class Album:
    id: str
    name: str
    release_date: str
    album_type: str
    total_tracks: int
    tracks: list[Track] = field(default_factory=list, repr=False)
    artists: list[Artist] = field(default_factory=list, repr=False)
    
    def __str__(self) -> str:
        def indent(text: str, prefix: str = "\t") -> str:
            return '\n'.join(prefix + line for line in text.split('\n'))
        
        # tracks_str = indent(str(self.album)) if self.album else "None"
        tracks_str = '\n'.join(indent(str(track)) for track in self.tracks) if len(self.tracks) else "\tTracks: None"
        artists_str = '\n'.join(indent(str(artist)) for artist in self.artists) if len(self.artists) else "\tArtists: None"
        
        return (
            f"Album: {self.name}, id: {self.id}\n"
            f"\trelease_date: {self.release_date}\n"
            f"\talbum_type: {self.album_type}\n"
            f"\ttotal_tracks: {self.total_tracks}\n"
            f"{tracks_str}\n"
            f"{artists_str}"
        )
