def normalize(self, track_raw: dict) -> dict:
    if not track_raw:
        return None

    track = track_raw.get("track", track_raw)
    if "item" in track:
        track = track["item"]
    if not track or not track.get("id"):
        return None

    norm_album = (
        source.album.normalize(track["album"], source)
        if track.get("album")
        else None
    )
    norm_artists = [
        source.artist.normalize(artist, source)
        for artist in (track.get("artists") or [])
    ]

    return {
        "id": track["id"],
        "name": track.get("name", ""),
        "duration_ms": track.get("duration_ms", 0),
        "is_local": track.get("is_local", False),
        "preview_url": track.get("preview_url"),
        "disc_number": track.get("disc_number", 1),
        "track_number": track.get("track_number", 0),
        "album": norm_album,
        "artists": norm_artists,
}