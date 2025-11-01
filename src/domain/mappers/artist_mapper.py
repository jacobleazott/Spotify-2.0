from src.models import Artist

def map_artist(artist_data: dict) -> Artist:
    return Artist(
        id   = artist_data["id"],
        name = artist_data["name"]
    )