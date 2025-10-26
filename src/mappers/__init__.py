# src/mappers/__init__.py
from __future__ import annotations

# Import *module-level* functions, not full modules
from .artist_mapper import normalize_artist_data, map_artist
from .track_mapper import normalize_track_data, map_track
from .album_mapper import normalize_album_data, map_album

__all__ = [
    "normalize_track_data",
    "normalize_album_data",
    "normalize_artist_data",
    "map_track",
    "map_album",
    "map_artist"
]