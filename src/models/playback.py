from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class Playback:
    track: Optional["Track"]
    device: Optional[str]
    progress_ms: Optional[int]
    is_playing: bool
    shuffle: Optional[str]
    repeat: Optional[str]
