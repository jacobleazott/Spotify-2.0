from .album_normalizer import AlbumNormalizer
from .artist_normalizer import ArtistNormalizer
from .track_normalizer import TrackNormalizer


class NormalizerCoordinator:
    def __init__(self):
        self.album_normalizer = AlbumNormalizer()
        self.artist_normalizer = ArtistNormalizer()
        self.track_normalizer = TrackNormalizer()

        