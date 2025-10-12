from dataclasses import dataclass
from typing import Optional
from artist import Artist
from album import Album

@dataclass
class Artist:
    id: str
    name: str