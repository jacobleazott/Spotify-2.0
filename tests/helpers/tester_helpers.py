# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    TESTER HELPERS                           CREATED: 2024-10-10          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# A collection of unit test helpers to create and manage our fake Spotify library we create to test with.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: artist_id - Id of our 'fake' artist.
       name - Name of our 'fake' artist/
OUTPUT: Artist dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_artist(artist_id: str, name: str) -> dict:
    return {
        'id': artist_id,
        'name': name
    }


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: album_id - Id of our 'fake' album.
       name - Name of our 'fake' album.
       artists - List of artist dictionaries see 'create_artist()'.
       album_type - Type of album values - "album", "single", "compilation"
OUTPUT: Album dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_album(album_id: str, name: str, artists: list[dict], album_type: str) -> dict:
    return {
        'id': album_id,
        'name': name,
        'artists': artists,
        'album_type': album_type,   # "album", "single", "compilation"
        'release_date': '0000-01-01'
    }


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: track_id - Id of our 'fake' track.
       name - Name of our 'fake' track.
       album - Album dict our track belongs to, see 'create_album()'.
       artists - List of artist dictionaries see 'create_artist()'.
       is_local - Bool on whether our track is local or not.
OUTPUT: Track dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_track(track_id: str, name: str, album: str, artists: list[dict], is_local: bool=False) -> dict:
    return {
        'id': track_id,
        'name': name,
        'album': album,
        'artists': artists,
        'is_local': is_local,
        'duration_ms': 1,
        'is_playable': True
    }


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: playlist_id - Id of our 'fake' playlist.
       name - Name of our 'fake' playlist.
       description - Description of our 'fake' playlist.
       tracks - List of track dicts, see 'create_track()'. This field is not in the actual response but is helpful for
                testing.
OUTPUT: Playlist dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_playlist(playlist_id: str, name: str, description: str, tracks: list[dict]) -> dict:
    return {
        'id': playlist_id,
        'name': name,
        'description': description,
        'tracks': tracks                # Note this isn't actually part of the playlist obj
    }


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: args - List of variables we wish to validate.
       types - List of python types the 'args' should be.
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_env(spotify_mocked):
    # Create Artists
    artist_no_tracks = create_artist('Ar001', 'Fake Artist 1')
    artist_only_theirs = create_artist('Ar002', 'Fake Artist 2')
    artist_followed = create_artist('Ar003', 'Fake Artist 3')
    artist_followed_appears_on = create_artist('Ar004', 'Fake Artist 4')
    artist_unfollowed_appears_on = create_artist('Ar005', 'Fake Artist 5')
    
    spotify_mocked.sp.artists += [artist_no_tracks, artist_only_theirs, artist_followed, artist_followed_appears_on
                                  , artist_unfollowed_appears_on]
    spotify_mocked.sp.user_artists += [artist_only_theirs, artist_followed, artist_followed_appears_on]
    
    # Create Albums
    al001 = create_album('Al001', 'Fake Album 1', [], 'album')
    al002 = create_album('Al002', 'Fake Album 2', [artist_only_theirs], 'album')
    al003 = create_album('Al003', 'Fake Album 3', [artist_only_theirs], 'single')
    al004 = create_album('Al004', 'Fake Album 4', [artist_only_theirs], 'compilation')
    
    al005 = create_album('Al005', 'Fake Album 5', [artist_followed], 'album')
    al006 = create_album('Al006', 'Fake Album 6', [artist_followed, artist_followed_appears_on], 'album')
    
    al007 = create_album('Al007', 'Fake Album 7', [artist_followed_appears_on], 'album')
    al008 = create_album('Al008', 'Fake Album 8', [artist_followed_appears_on, artist_unfollowed_appears_on], 'album')
    
    al009 = create_album('Al009', 'Fake Album 8', [artist_unfollowed_appears_on], 'single')
    al010 = create_album('Al010', 'Fake Album 10', [artist_unfollowed_appears_on], 'album')
    
    spotify_mocked.sp.env_albums += [al001, al002, al003, al004, al005, al006, al007, al008, al009, al010]

    # Create Tracks
    local_artist = create_artist(None, 'Fake Local Artist 1')
    local_album = create_album(None, 'Fake Local Album 1', [], None)
    local_track = create_track(None, 'Fake Local Track 1', local_album, [local_artist], is_local=True)
    
    tr001 = create_track('Tr001', 'Fake Track 1', al002, [artist_only_theirs])
    tr002 = create_track('Tr002', 'Fake Track 2', al002, [artist_only_theirs])
    tr003 = create_track('Tr003', 'Fake Track 3', al003, [artist_only_theirs])
    tr004 = create_track('Tr004', 'Fake Track 4', al004, [artist_only_theirs])
    
    tr005 = create_track('Tr005', 'Fake Track 5', al005, [artist_followed])
    tr006 = create_track('Tr006', 'Fake Track 6', al006, [artist_followed])
    tr007 = create_track('Tr007', 'Fake Track 7', al006, [artist_followed, artist_followed_appears_on])
    
    tr008 = create_track('Tr008', 'Fake Track 8', al007, [artist_followed_appears_on])
    tr009 = create_track('Tr009', 'Fake Track 9', al007, [artist_followed_appears_on])
    tr010 = create_track('Tr010', 'Fake Track 10', al008, [artist_followed_appears_on])
    tr011 = create_track('Tr011', 'Fake Track 11', al008, [artist_unfollowed_appears_on])
    tr012 = create_track('Tr012', 'Fake Track 12', al008, [artist_followed_appears_on, artist_unfollowed_appears_on])
    
    tr013 = create_track('Tr013', 'Fake Track 13', al009, [artist_unfollowed_appears_on])
    tr014 = create_track('Tr014', 'Fake Track 14', al010, [artist_unfollowed_appears_on])
    tr015 = create_track('Tr015', 'Fake Track 15', al010, [artist_unfollowed_appears_on, artist_followed_appears_on])

    spotify_mocked.sp.tracks += [local_track, tr001, tr002, tr003, tr004, tr005, tr006, tr007, tr008
                                 , tr009, tr010, tr011, tr012, tr013, tr014, tr015]

    # Create Playlists
    spotify_mocked.sp.playlists.append(create_playlist('Pl001', 'Fake Playlist 1', 'description 1', []))
    spotify_mocked.sp.playlists.append(create_playlist('Pl002', 'Fake Playlist 2', 'description 2'
                                                       , [tr002, tr003, tr004]))
    spotify_mocked.sp.playlists.append(create_playlist('Pl003', 'Fake Playlist 3', 'description 3'
                                                       , [tr008, tr011, tr012, tr015]))
    spotify_mocked.sp.playlists.append(create_playlist('Pl004', 'Fake Playlist 4', 'description 4'
                                                       , [local_track, local_track, tr001, tr001]))


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════