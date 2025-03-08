# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIPY MOCK                             CREATED: 2024-09-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# If we want to be able to unit test any of GSH and even a lot of our features then any api requests really need to 
#   be mocked so that we can percisely control what is coming across to hit all of our test stepsdef  As long as we 
#   mock each function in our class here when we override the import things should all work as intendeddef  
# Docs - https://spotipy.readthedocs.io/en/2.24.0/
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import tests.helpers.api_response_test_messages as artm
from src.helpers.decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that can be used to override 'spotipy' import. Not all functions are implemented or even present.
             Any additional features added into GSH should be added here for unit testing.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MockedSpotipyProxy():

    def __init__(self, logger: logging.Logger=None):
        self.user_id = 'Us000'
        self.user_queue, self.prev_songs, self.user_artists, self.artists, \
            self.env_albums, self.tracks, self.playlists = [], [], [], [], [], [], []
        
        self.current_user_followed_artists_response = artm.current_user_followed_artists_test_message.copy()
        self.current_user_playlists_response = artm.current_user_playlists_test_message.copy()
        self.current_playback_response = artm.current_playback_test_message.copy()
        
        # self.playlist_items_lookup_table = artm.playlist_items_lookup_table_test.copy()
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MOCK HELPER METHODS ═════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ORIGINAL SPOTIPY METHODS ════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
    def next(self, response):
        ret = None
        if "next" in response:
            ret = response['next']
        else:
            for key, field in list(response.items()):
                if "next" in response[key]:
                    ret = response[key]['next']
                    break
        return ret
        
    def current_user_followed_artists(self, limit=50, after=None):
        self.current_user_followed_artists_response['artists']['items'] = self.user_artists
        return self.current_user_followed_artists_response
    
    def current_user_playlists(self, limit=50, offset=0):
        self.current_user_playlists_response['items'] = self.playlists
        return self.current_user_playlists_response
        
    def current_playback(self, market=None, additional_types=None):
        return self.current_playback_response
    
    def pause_playback(self, device_id=None):
        self.current_playback_response['is_playing'] = False
        return None
    
    def next_track(self, device_id=None):
        self.prev_songs.append(self.current_playback_response['item'])
        self.current_playback_response['is_playing'] = True
        if len(self.user_queue) > 0:
            self.current_playback_response['item'] = self.user_queue.pop(0)
        else:
            self.current_playback_response['item'] = artm.track_test.copy()
            
        return None
    
    def previous_track(self, device_id=None):
        self.current_playback_response['is_playing'] = True
        if len(self.prev_songs) > 1:
            self.current_playback_response['item'] = self.prev_songs.pop(-1)
        else:
            self.current_playback_response['item'] = artm.track_test.copy()
            
        return None
        
    def shuffle(self, state, device_id=None):
        self.current_playback_response['shuffle_state'] = state
        return None
    
    def repeat(self, state, device_id=None):
        self.current_playback_response['repeat_state'] = state
        return None
    
    def add_to_queue(self, uri, device_id=None):
        self.user_queue.append(uri)
        return None
        
    def playlist_add_items(self, playlist_id, items, position=None):
        track_objects = [track for track in self.tracks if track['id'] in items]
        if len(track_objects) != len(items):
            raise Exception(f"playlist_add_items: not all tracks found, track_objects: {len(track_objects)}, items: {len(items)}")
        
        for track_obj in track_objects:
            self.playlist(playlist_id)['tracks'].append(track_obj)
            
        return None
        
    def playlist_items(self, playlist_id, fields=None, limit=100, offset=0, market=None, additional_types=('track', 'episode')):
        response = artm.playlist_items_test_message.copy()
        for track in self.playlist(playlist_id)['tracks']:
            tmp_item = artm.playlist_item_test.copy()
            tmp_item['track'] = track.copy()
            response['items'] = response['items'] + [tmp_item]
            
        return response
        
    def user_playlist_create(self, user, name, public=True, collaborative=False, description=''):
        tmp_playlist = artm.playlist_test.copy()
        tmp_playlist['id'] = f"Pl{len(self.playlists)+1:03d}"
        tmp_playlist['name'] = name
        tmp_playlist['public'] = public
        tmp_playlist['collaborative'] = collaborative
        tmp_playlist['description'] = description
        
        self.playlists.append(tmp_playlist)
        # self.playlist_items_lookup_table[tmp_playlist['id']] = []
        
        return tmp_playlist
        
    def playlist_change_details(self, playlist_id, name=None, public=None, collaborative=None, description=None):
        playlist = self.playlist(playlist_id)
        
        if name is not None:
            playlist['name'] = name
        if public is not None:
            playlist['public'] = public
        if collaborative is not None:
            playlist['collaborative'] = collaborative
        if description is not None:
            playlist['description'] = description
            
        return None
        
    def playlist_remove_all_occurrences_of_items(self, playlist_id, items, snapshot_id=None):
        playlist_items = self.playlist(playlist_id)['tracks']
        self.playlist(playlist_id)['tracks'] = [item for item in playlist_items if not item['id'] in items]
        return None
        
    def artist_albums(self, artist_id, album_type=None, include_groups=None, country=None, limit=20, offset=0):
        # (album, single, compilation, appears_on)
        artist_album_list = []
        for album in self.env_albums:
            album_group = album['album_group'] if 'album_group' in album else album['album_type']
            if include_groups is not None and not album_group in include_groups:
                continue
            for artist in album['artists']:
                if artist['id'] == artist_id:
                    artist_album_list.append(album)
                    break
        artist_album_response = artm.artist_albums_test_message.copy()
        artist_album_response['items'] = [artm.full_album_to_simple(album, album_group=album_group) 
                                          for album in artist_album_list]

        return artist_album_response
        
    def search(self, q, limit=10, offset=0, type='track', market=None):
        # Right now the only time we search is for validating appears_on tracks which isn't even supported 
        #   in the artist_albums for us to edit right now.
        return "NOT IMPLEMENTED"
    
    def track(self, track_id, market=None):
        return next((track for track in self.tracks if track_id == track['id']), None)

    def artist(self, artist_id, market=None):
        return next((artist for artist in self.artists if artist_id == artist['id']), None)
        
    def album(self, album_id, market=None):
        return next((album for album in self.env_albums if album_id == album['id']), None)
    
    def albums(self, albums, market=None):
        # need to add a 'tracks' and 'items' sub folder into this that contains the track objects for this album
        albums_list = []
        for album_id in albums:
            tmp_album = self.album(album_id).copy()
            tmp_album['tracks'] = {}
            tmp_album['tracks']['items'] = [self.track(track['id']) for track in self.tracks if track['album']['id'] == album_id]
            albums_list.append(tmp_album)
        return {'albums': albums_list}
        
    def playlist(self, playlist_id, fields=None, market=None, additional_types=('track',)):
        return next((playlist for playlist in self.playlists if playlist_id == playlist['id']), None)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════