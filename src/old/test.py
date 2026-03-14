from domain.models import Album, Artist, Track, Playlist, Playback

def build_album(album_raw: dict) -> Album:
    if not album_raw or not album_raw.get("id"):
        return None

    tracks = [build_track(artist) for artist in (album_raw.get("tracks", {}).get("items", []))]
    artists = [build_artist(artist) for artist in (album_raw.get("artists", []))]

    return Album(
        id=album_raw["id"],
        name=album_raw.get("name", ""),
        release_date=album_raw.get("release_date", ""),
        album_type=album_raw.get("album_type", ""),
        total_tracks=album_raw.get("total_tracks", 0),
        tracks=tracks,
        artists=artists,
    )


def build_artist(artist_raw: dict) -> Artist:
    if not artist_raw or not artist_raw.get("id"):
        return None
    
    return Artist(
        id=artist_raw["id"],
        name=artist_raw.get("name", ""),
    )

def build_track(track_raw: dict) -> Track:
        if not track_raw:
            return None
        
        if 'track' in track_raw:
            track_raw = track_raw['track']
        if 'item' in track_raw:
            track_raw = track_raw['item']

        if not track_raw or not track_raw.get("id"):
            return None
        
        album = build_album(track_raw.get("album"))
        artists = [build_artist(artist) for artist in (track_raw.get("artists", []))]

        return Track(
            id=track_raw["id"],
            name=track_raw.get("name"),
            duration_ms=track_raw.get("duration_ms"),
            is_local=track_raw.get("is_local"),
            is_playable=(track_raw.get("preview_url") is not None),
            disc_number=track_raw.get("disc_number"),
            track_number=track_raw.get("track_number"),
            album=album,
            artists=artists,
        )


def build_playlist(playlist_raw: dict) -> Playlist:
    if not playlist_raw or not playlist_raw.get("id"):
        return None
    
    tracks = [build_track(track) for track in playlist_raw.get("tracks", {}).get("items", [])]
    
    return Playlist(
        id=playlist_raw["id"],
        name=playlist_raw.get("name"),
        description=playlist_raw.get("description"),
        snapshot_id=playlist_raw.get("snapshot_id", ""),
        total_tracks=playlist_raw.get("tracks", {}).get("total", 0),
        tracks=tracks
    )

def build_playback(playback_raw: dict) -> dict:
    if not playback_raw:
        return None
    

    return playback_raw

from pathlib import Path
import json

if __name__ == "__main__":
    current_dir = Path(__file__).parent

    def test_several_tracks():
        with open(current_dir / "../../tests/sample_responses/tracks/get_several_tracks.json", "r") as f:
            data = json.load(f)
            for track in data['tracks']:
                print(build_track(track))

    def test_track():
        with open(current_dir / "../../tests/sample_responses/tracks/get_track.json", "r") as f:
            data = json.load(f)
            print(build_track(data))

    def test_track_recommendations():
        with open(current_dir / "../../tests/sample_responses/tracks/get_recommendations.json", "r") as f:
            data = json.load(f)
            for track in data['tracks']:
                print(build_track(track))

    def test_user_saved_tracks():
        with open(current_dir / "../../tests/sample_responses/tracks/get_users_saved_tracks.json", "r") as f:
            data = json.load(f)
            for track in data['items']:
                print(build_track(track))

    def test_album():
        with open(current_dir / "../../tests/sample_responses/albums/get_album.json", "r") as f:
            data = json.load(f)
            print(build_album(data))

    def test_several_albums():
        with open(current_dir / "../../tests/sample_responses/albums/get_several_albums.json", "r") as f:
            data = json.load(f)
            for album in data['albums']:
                print(build_album(album))

    def test_get_album_tracks():
        with open(current_dir / "../../tests/sample_responses/albums/get_album_tracks.json", "r") as f:
            data = json.load(f)
            for track in data['items']:
                print(build_track(track))

    def test_artist():
        with open(current_dir / "../../tests/sample_responses/artists/get_artist.json", "r") as f:
            data = json.load(f)
            print(build_artist(data))

    def test_several_artists():
        with open(current_dir / "../../tests/sample_responses/artists/get_several_artists.json", "r") as f:
            data = json.load(f)
            for artist in data['artists']:
                print(build_artist(artist))

    def test_artists_related_artists():
        with open(current_dir / "../../tests/sample_responses/artists/get_artists_related_artists.json", "r") as f:
            data = json.load(f)
            for artist in data['artists']:
                print(build_artist(artist))

    def test_create_playlist():
        with open(current_dir / "../../tests/sample_responses/playlists/create_playlist.json", "r") as f:
            data = json.load(f)
            print(build_playlist(data))

    def test_playlist():
        with open(current_dir / "../../tests/sample_responses/playlists/get_playlist.json", "r") as f:
            data = json.load(f)
            print(build_playlist(data))

    def test_playlist_items():
        with open(current_dir / "../../tests/sample_responses/playlists/get_playlist_items.json", "r") as f:
            data = json.load(f)
            for track in data['items']:
                print(build_track(track))

    def test_users_playlists():
        with open(current_dir / "../../tests/sample_responses/playlists/get_users_playlists.json", "r") as f:
            data = json.load(f)
            for playlist in data['items']:
                print(build_playlist(playlist))

    def test_current_users_playlists():
        with open(current_dir / "../../tests/sample_responses/playlists/get_current_users_playlists.json", "r") as f:
            data = json.load(f)
            for playlist in data['items']:
                print(build_playlist(playlist))
                
    def test_current_user_profile():
        with open(current_dir / "../../tests/sample_responses/users/get_current_user_profile.json", "r") as f:
            data = json.load(f)
            print(build_user(data))

    def test_user_followed_artists():
        with open(current_dir / "../../tests/sample_responses/users/get_followed_artists.json", "r") as f:
            data = json.load(f)
            for artist in data['artists']['items']:
                print(build_artist(artist))

    def test_user_top_artists():
        with open(current_dir / "../../tests/sample_responses/users/get_users_top_items_artists.json", "r") as f:
            data = json.load(f)
            for artist in data['items']:
                print(build_artist(artist))

    def test_user_top_tracks():
        with open(current_dir / "../../tests/sample_responses/users/get_users_top_items_tracks.json", "r") as f:
            data = json.load(f)
            for track in data['items']:
                print(build_track(track))

    # test_several_tracks()
    # print("\n ###################################################################### \n")
    # test_track()
    # print("\n ###################################################################### \n")
    # test_track_recommendations()
    # print("\n ###################################################################### \n")
    # test_user_saved_tracks()
    # print("\n ###################################################################### \n")
    # test_album()
    # print("\n ###################################################################### \n")
    # test_several_albums()
    # print("\n ###################################################################### \n")
    # test_get_album_tracks()
    # print("\n ###################################################################### \n")
    # test_artist()
    # print("\n ###################################################################### \n")
    # test_several_artists()
    # print("\n ###################################################################### \n")
    # test_artists_related_artists()
    # print("\n ###################################################################### \n")
    # test_create_playlist()
    # print("\n ###################################################################### \n")
    test_playlist()
    print("\n ###################################################################### \n")
    test_playlist_items()
    # print("\n ###################################################################### \n")
    # test_users_playlists()
    # print("\n ###################################################################### \n")
    # test_current_users_playlists()
    # print("\n ###################################################################### \n")
    # # test_current_user_profile()
    # print("\n ###################################################################### \n")
    # test_user_followed_artists()
    # print("\n ###################################################################### \n")
    # # data_path = current_dir / "../../tests/sample_responses/users/get_users_profile.json"
    # print("\n ###################################################################### \n")
    # test_user_top_artists()
    # print("\n ###################################################################### \n")
    # test_user_top_tracks()
    # print("\n ###################################################################### \n")

    # print("\n ###################################################################### \n")


    # Build the path to data.json relative to this file

    ######### TRACK RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_several_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_track.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_recommendations.json"      
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_users_saved_tracks.json"

    ######### ALBUM RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/albums/get_album_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/albums/get_album.json"
    # data_path = current_dir / "../../tests/sample_responses/albums/get_several_albums.json"

    ######### ARTIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artist.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_albums.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_related_artists.json"

    ######### PLAYLIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/playlists/create_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist_items.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_users_playlists.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_current_users_playlists.json"

    ######### USER RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/users/get_current_users_profile.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_followed_artists.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_profile.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_top_items_artists.json"
    # data_path = current_dir / "../../tests/sample_responses/users/get_users_top_items_tracks.json"

    ######### PLAYER RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/player/get_currently_playing_track.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_playback_state.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_recently_played_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/player/get_users_queue.json"