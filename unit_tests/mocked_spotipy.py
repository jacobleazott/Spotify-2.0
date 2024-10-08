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
import api_response_test_messages as artm
import logging as log
import sys

sys.path.insert(1, '/home/jaleazo/projects/Spotify_Release_Pi/src')
from decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that can be used to override 'spotipy' import. Not all functions are implemented or even present.
             Any additional features added into GSH should be added here for unit testing.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Spotify(LogAllMethods):
    user_id = 'Us000'
    user_queue, prev_songs, user_artists, artists, albums, tracks, playlists = [], [], [], [], [], [], []
    
    current_user_followed_artists_response = artm.current_user_followed_artists_test_message.copy()
    current_user_playlists_response = artm.current_user_playlists_test_message.copy()
    current_playback_response = artm.current_playback_test_message.copy()
    
    playlist_items_lookup_table = artm.playlist_items_lookup_table_test.copy()

    def __init__(self, auth_manager=None):
        return None
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MOCK HELPER METHODS ═════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ORIGINAL SPOTIPY METHODS ════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
    def next(self, response):
        return None
        
    def current_user_followed_artists(self, limit=50, after=None):
        self.current_user_followed_artists_response['artists']['items'] = user_artists
        return self.current_user_followed_artists_response
    
    def current_user_playlists(self, limit=50, offset=0):
        user_playlists = [playlist for playlist in self.playlists if playlist['owner']['id'] == user_id]
        self.current_user_playlists_response['items'] = user_playlists
        return self.current_user_playlists_response
        
    def current_playback(self, market=None, additional_types=None):
        return self.current_playback_response
    
    def pause_playback(self, device_id=None):
        self.current_playback_response['is_playing'] = False
        return None
    
    def next_track(self, device_id=None):
        self.prev_songs.append(self.current_playback_response['item'])
        self.current_playback_response['is_playing'] = True
        if len(self.user_queue) > 1:
            self.current_playback_response['item'] = self.user_queue.pop(0)
        else:
            self.current_playback_response['item'] = artm.track_test.copy()
            
        return None
    
    def previous_track(self, device_id=None):
        self.current_playback_response['is_playing'] = True
        if len(prev_songs) > 1:
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
        
        playlist_items_list = self.playlist_items_lookup_table[playlist_id]
        
        for track_obj in track_objects:
            playlist_item_tmp = artm.playlist_item_test.copy()
            playlist_item_tmp['track'] = track_obj
            playlist_items_list.append(playlist_item_tmp)
            
        return None
        
    def playlist_items(self, playlist_id, fields=None, limit=100, offset=0, market=None, additional_types=('track', 'episode')):
        return self.playlist_items_response[playlist_id]
        
    def user_playlist_create(self, user, name, public=True, collaborative=False, description=''):
                  description={description})")
        tmp_playlist = artm.playlist_test.copy()
        tmp_playlist['id'] = f"Pl{len(self.playlists):03d}"
        tmp_playlist['owner']['id'] = user
        tmp_playlist['name'] = name
        tmp_playlist['public'] = public
        tmp_playlist['collaborative'] = collaborative
        tmp_playlist['description'] = description
        
        self.playlists.append(tmp_playlist)
        self.playlist_items_lookup_table[tmp_playlist['id']] = []
        
        return tmp_playlist['id']
        
    def user_playlist_change_details(self, user, playlist_id, name=None, public=None, collaborative=None, description=None):
        playlist = self.playlist(playlist_id)
        
        if name is not None:
            self.playlist['name'] = name
        if public is not None:
            self.playlist['public'] = public
        if collaborative is not None:
            self.playlist['collaborative'] = collaborative
        if description is not None:
            self.playlist['description'] = description
            
        return None
        
    def playlist_remove_all_occurrences_of_items(self, playlist_id, items, snapshot_id=None):
        playlist_items = self.playlist_items_lookup_table[playlist_id]
        playlist_items = [item for item in playlist_items if not item['track']['id'] in items]
        
        return None
        
    # TODO - We do not have a current way to tell 
    def artist_albums(self, artist_id, album_type=None, include_groups=None, country=None, limit=20, offset=0):
        artist_album_list = []
        for album in self.albums:
            if album_type is not None and not album['album_type'] in album_type:
                continue
            for artist in album['artists']:
                if artist['id'] == artist_id:
                    artist_album_list.append(album)
                    break
        artist_album_response = artm.artist_albums_test_message.copy()
        artist_album_response['items'] = [artm.full_album_to_simple(album, album_group=album['album_group']) 
                                          for album in artist_album_list]

        return artist_album_response
        
    def search(self, q, limit=10, offset=0, type='track', market=None):
        # Right now the only time we search is for validating appears_on tracks which isn't even supported 
        #   in the artist_albums for us to edit right now.
        return "NOT IMPLEMENTED"
    
    def track(self, track_id, market=None):
        return next((track for track in self.tracks if track_id == track['id']), None)

    def artist(self, artist_id):
        return next((artist for artist in self.artists if artist_id == artist['id']), None)
        
    def album(self, album_id, market=None):
        return next((album for album in self.albums if album_id == album['id']), None)
        
    def playlist(self, playlist_id, fields=None, market=None, additional_types=('track',)):
        return next((playlist for playlist in self.playlists if playlist_id == playlist['id']), None)


class oauth2:
    def SpotifyOAuth(scope=None, username=None, open_browser=None):
        return None
    
# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
