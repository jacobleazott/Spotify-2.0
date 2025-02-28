# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIFY API RESPONSE TEST MESSAGES       CREATED: 2024-09-19          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# As part of mocking 'spotipy' or the spotify API in general we need to create quite a few fake messages, artists,
#   tracks, and the like. Here we just create some simple functions for translating 'full' objects to 'simple' objects
#   and define the structure of all necessary API responses. These can then be used to create any number of fake 
#   objects and responses for all of our unit testing needs.
# 
# Note that a lot of the test messages have commented out fields. These are fields that Spotify does return but the
#   code simply doesn't reference them. They have been commented out to make testing more direct and concise.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Some of the spotify responses give a 'simplified' artist object instead of the full one. This is just a 
    subset of fields from a 'full' object. So we just create a new dict with only those fields
    https://developer.spotify.com/documentation/web-api/reference/get-an-album
INPUT: full_artist_dict - 'full' artist object we will turn into a 'simple' one, creates a full copy
OUTPUT: a 'simple' artist dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def full_artist_to_simple(full_artist_dict):
    return dict((k, full_artist_dict[k]) for k in('external_urls', 'href', 'id', 'name', 'type', 'uri'))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Stupidest thing, but the "simple" album object has an additional field to the "normal" album object
    which is album_group which just gives 'relation' of the artist to the album, ie. it's only different from the 
    album_type if the artist 'appears_on' the album ie doesn't have artist creds on the album itself but shows up in 
    one of the tracks.
    https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
INPUT: full_album - the 'album_test' dict we will create into a 'simple' object, creates a full copy
       album_group - what type of 'relation' this album is to the artist. (album, single, compilation, appears_on)
OUTPUT: a 'simple' album dict
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def full_album_to_simple(full_album_dict, album_group='album'):
    tmp_album_simple = full_album_dict.copy()
    tmp_album_simple['album_group'] = album_group
    return tmp_album_simple

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# BASE OBJECT TEST MESSAGES ═══════════════════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
fake_user = {
    # 'display_name': 'fake user 1',
    # 'external_urls': {'spotify': 'playlist_owner_spotify_url'},
    # 'href': 'playlist_owner_href',
    # 'id': 'Us000',
    # 'type': 'user',
    # 'uri': 'spotify:user:'
    }

artist_full_test = {
    # 'external_urls': {'spotify': 'artist_spotify_url'},
    # 'followers': {'href': None, 'total': 100000},
    # 'genres': ['fake genre 1'],
    # 'href': 'artist_href',
    'id': 'Ar000',
    # 'images': [],
    'name': 'Fake Artist 0',
    # 'popularity': 0,
    # 'type': 'artist',
    # 'uri': 'spotify:artist:'
    }

album_test = {
    'album_type': 'album',      # "album", "single", "compilation"
    'artists': [artist_full_test],
    # 'available_markets': ['US'],
    # 'external_urls': {'spotify': 'album_spotify_url'},
    # 'href': 'album_href', 
    'id': 'Al000',
    # 'images': [],
    'name': 'Fake Album 0',
    'release_date': '0000-01-01',
    # 'release_date_precision': 'day',
    # 'total_tracks': 0,
    # 'type': 'album',
    # 'uri': 'spotify:album:'
    }

track_test = {
    'album': album_test,
    'artists': [artist_full_test],
    # 'available_markets': ['US'],
    # 'disc_number': 0,
    'duration_ms': 0,
    # 'explicit': False,
    # 'external_ids': {'isrc': 'fake_isrc'},
    # 'external_urls': {'spotify': 'track_spotify_url'},
    # 'href': 'track_href',
    'id': 'Tr000',
    'is_local': False,
    'name': 'Fake Track 0',
    'is_playable': True,
    # 'popularity': 0,
    # 'preview_url': 'spotify_preview_url',
    # 'track_number': 0,
    # 'type': 'track',
    # 'uri': 'spotify:track:'
    }

playlist_test = {
    # 'collaborative': False,
    'description': 'fake playlist description',
    # 'external_urls': {'spotify': 'playlist_spotify_url'},
    # 'href': 'playlist_href',
    'id': 'Pl000',
    # 'images': [],
    'name': 'Fake Playlist 0',
    # 'owner': fake_user,
    # 'primary_color': None,
    # 'public': True,
    # 'snapshot_id': 'A000/B000',
    # 'tracks': {'href': 'playlist_tracks_href','total': 1},
    # 'type': 'playlist',
    # 'uri': 'spotify:playlist:'
    'tracks': []                    # THIS FIELD DOESN'T EXIST, JUST FOR TESTING
    }

playlist_item_test = {
    # 'added_at': '0000-01-01T00:00:00',
    # 'added_by': fake_user,               # NOTE THIS ADDED_BY CAN BE NULL AND DOESN'T HAVE 'display_name'
    'is_local': False,
    # 'primary_color': None,
    'track': track_test,
    # 'video_thumbnail': {'url': None}
    }

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# RESPONSE OBJECT TESTS ═══════════════════════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
current_user_followed_artists_test_message = {
    'artists': {
        # 'cursors': {'after': 'fake_cursor_after'},
        # 'href': 'current_user_followed_artists_href',
        'items': [artist_full_test],
        # 'limit': 1,
        'next': None,
        # 'total': 1}
    }}

current_user_playlists_test_message = {
    # 'href': 'current_user_playlists_href',
    'items': [playlist_test],
    # 'limit': 1,
    'next': None,
    # 'offset': 0,
    # 'previous': None,
    # 'total': 0
    }

current_playback_test_message = {
    # 'actions': {'disallows': {'resuming': True}},
    'context': {
                # 'external_urls': {'spotify': 'current_playback_url'},
                # 'href': 'current_playback_href',
                'type': 'playlist',
                'uri': 'spotify:playlist:Pl001'},
    'currently_playing_type': 'track',
    # 'device': {'id': 'De000',
    #             'is_active': True,
    #             'is_private_session': False,
    #             'is_restricted': False,
    #             'name': 'fake_device',
    #             'supports_volume': True,
    #             'type': 'Computer',
    #             'volume_percent': 0},
    'is_playing': True,
    'item': track_test,
    # 'progress_ms': 0,
    'repeat_state': 'off',
    'shuffle_state': False,
    # 'smart_shuffle': False,
    # 'timestamp': 0
    }

get_playback_state_test_message = {
    'context': {'type': 'playlist',
                'id': 'Pl001'},
    'currently_playing_type': 'track',
    'is_playing': True,
    'repeat_state': 'off',
    'shuffle_state': False,
    'track': {'id': "Tr001",
             'name': "Fake Track 1",
             'artists': [{'id': 'Ar001',
                           'track': 'Fake Artist 1'}]}
    }

playlist_items_test_message = {
    # 'href': 'playlist_items_href',
    'items': [],    # playlist_item_test
    # 'limit': 1,
    'next': None,
    # 'offset': 0,
    # 'previous': None,
    # 'total': 0
    }

artist_albums_test_message = {
    # 'href': 'artist_albums_href',
    'items': [full_album_to_simple(album_test, album_group='album')],
    # 'limit': 1, 
    'next': None,
    # 'offset': 0,
    # 'previous': None,
    # 'total': 0
    }


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════