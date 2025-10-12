from dataclasses import dataclass
from typing import Optional
from Artist import Artist
from Album import Album

@dataclass
class Artist:
    id: str
    name: str