from dataclasses import dataclass, field

from .track import Track

@dataclass
class Playlist:
    id: str
    name: str
    description: str
    snapshot_id: str
    total_tracks: int
    tracks: list[Track] = field(default_factory=list, repr=False)


    def __str__(self) -> str:
        def indent(text: str, prefix: str = "\t") -> str:
            return '\n'.join(prefix + line for line in text.split('\n'))
        
        # tracks_str = indent(str(self.album)) if self.album else "None"
        tracks_str = '\n'.join(indent(str(track)) for track in self.tracks) if len(self.tracks) else "\tTracks: None"
        
        return (
            f"Playlist: {self.name}, id: {self.id}\n"
            f"\tdescription: {self.description}\n"
            f"\tsnapshot_id: {self.snapshot_id}\n"
            f"\ttotal_tracks: {self.total_tracks}\n"
            f"{tracks_str}"
        )