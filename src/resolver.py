from src.models import Track, Album, Artist
from src.sources import abstract_source

class DataResolver:
    def __init__(self, source: abstract_source):
        self.source = source
        self.track_cache = {}
        self.artist_cache = {}
        self.album_cache = {}

    def resolve_track(self, track_id: str) -> Track:
        return self.resolve_tracks([track_id])[0]
    
    # This seems to be pretty boilerplate
    # Check if it's ids or data dicts
    #   If its id's
    #       Check cache for id's 
    #       Grab from source rest of data
    #   If its data
    #       Check cache for id's
    #       add to list
    # Use same list, normalize, map, add to cache, return

    # A few things would be on hydration, should hydration be different? Probably? Just verifying all data is there
    # Can probably rip out all the logic for checking the cache, and grabbing the data to be model agnostic
    #   Honestly could do the same if we somehow knew how to map grabbing from source, normalizing, and mapping to their model
        
    def resolve_tracks(self, tracks_data: list[str] | list[dict]) -> list[Track]:
        resolved_tracks = []
        unresolved_tracks = []
        if isinstance(tracks_data[0], str):
            for track_id in tracks_data:
                if track_id in self.track_cache:
                    resolved_tracks.append(self.track_cache[track_id])
                else:
                    unresolved_tracks.append(track_id)

            raw_tracks_data = self.source.get_tracks(unresolved_tracks)
        else:
            for track_data in tracks_data:
                if track_data['id'] in self.track_cache:
                    resolved_tracks.append(self.track_cache[track_data['id']])
                else:
                    unresolved_tracks.append(track_data)
            raw_tracks_data = tracks_data

        for raw_track in raw_tracks_data:
            norm = self.source.normalize_track(raw_track)
            track = map_track(norm, self)
            resolved_tracks.append(track)
            self.cache[track.id] = track

        return resolved_tracks
    
    def hydrate_tracks(self, tracks: list[Track]):
        # Need to check that all "necessary" data is here... how we deem necessary data is going to be... questionable at best
        # Fuck also need to be careful with resolving to not continue to do it recursively, ideally all it would stop because of our cache...
        # I think just instead of resolving everything we need to be selective
        # So when we call like a get_track, get_album, etc... it NEEDS to return at least the id of its relationship. 
        #   Don't resolve just the id, that's for the hydrator to worry about
        #   Resolve any raw data we get but that means that like album would not have it's tracks id's when we grab an album from a track
        # So 3 cases need to be handled
        #   raw_data is given
        #   id is given
        #   Nothing is given
        # In the case of raw_data we have to ask ourselves the same question for all "nested" items
        # The other two cases we will have to grab the data. Where the id is straight forward but the none is... different
        # The none requires us to know more context in how to grab the data. Like if we have no tracks for an album we can call
        #   get_album
        #   get_albums
        #   get_album_tracks
        # and then same issue for playlists but that is in the PlaylistService
        # This is all problematic because of the relationship between albums and tracks and that they reference each other.
        # 
        pass

    def resolve_album(self, album_data: dict | str) -> Album:
        # handle either a dict (embedded) or id (lazy load)
        if isinstance(album_data, dict):
            album_id = album_data["id"]
            if album_id in self.cache:
                return self.cache[album_id]
            album = map_album(album_data, self)
            self.cache[album_id] = album
            return album
        else:
            album_id = album_data
            if album_id in self.cache:
                return self.cache[album_id]
            raw = self._get_from_sources("get_album", album_id)
            norm = normalize_album_data(raw)
            album = map_album(norm, self)
            self.cache[album.id] = album
            return album

    def resolve_artist(self, artist_data: dict | str) -> Artist:
        if isinstance(artist_data, dict):
            artist_id = artist_data["id"]
            if artist_id in self.cache:
                return self.cache[artist_id]
            artist = map_artist(artist_data)
            self.cache[artist_id] = artist
            return artist
        else:
            artist_id = artist_data
            if artist_id in self.cache:
                return self.cache[artist_id]
            raw = self._get_from_sources("get_artist", artist_id)
            norm = normalize_artist_data(raw)
            artist = map_artist(norm)
            self.cache[artist.id] = artist
            return artist

    def _get_from_sources(self, method_name, id_):
        for s in self.sources:
            method = getattr(s, method_name, None)
            if method:
                data = method(id_)
                if data:
                    return data
        raise LookupError(f"{method_name} failed for {id_}")

##########################################################################################33
def map_track(data: dict, resolver: DataResolver) -> Track:
    album = resolver.resolve_album(data["album"])  # may already have embedded info
    artists = [resolver.resolve_artist(a) for a in data["artists"]]
    return Track(
        id=data["id"],
        name=data["name"],
        album=album,
        artists=artists,
    )