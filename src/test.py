if __name__ == "__main__":
    current_dir = Path(__file__).parent

    # Build the path to data.json relative to this file

    ######### TRACK RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_several_tracks.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_track.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_recommendations.json"
    # data_path = current_dir / "../../tests/sample_responses/tracks/get_users_saved_tracks.json"

    ######### ALBUM RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/albums/get_album_tracks.json"
    data_path = current_dir / "../../tests/sample_responses/albums/get_album.json"
    # data_path = current_dir / "../../tests/sample_responses/albums/get_several_albums.json"

    ######### ARTIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artist.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_albums.json"
    # data_path = current_dir / "../../tests/sample_responses/artist/get_artists_related_artists.json"

    ######### PLAYLIST RESPONSES
    # data_path = current_dir / "../../tests/sample_responses/playlists/create_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_current_users_playlists.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist_items.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_playlist.json"
    # data_path = current_dir / "../../tests/sample_responses/playlists/get_users_playlists.json"

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

    # Load JSON safely
    with data_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # tracks = process_get_track(data)
    # tracks = process_get_album_tracks("my_album_id", data['albums'][0]['tracks'])
    tracks = process_get_album(data)
    
    for track in tracks:
        print(track)
        print(track.album)
        for artist in track.artists:
            print(artist)