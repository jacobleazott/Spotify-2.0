# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIFY API HELPERS                      CREATED: 2024-01-05          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This class is a fundamentally just a wrapper around spotipy to fit our needs specifically. It handles our token
#   info and you just need to call the class with the scope you wish to use. It handles the rest. The class should
#   only include "general" methods for grabbing data and formatting it.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import calendar
import inspect
import logging
import os
import time

from datetime  import datetime
from functools import wraps
from typing    import Any, Dict, List, Optional, Union

from src.helpers.decorators  import *
from src.helpers.Settings    import Settings
from src.proxy.Spotipy_Proxy import SpotipyProxy

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Validates that the given 'args' are of type 'types'.
INPUT: args - List of variables we wish to validate.
       types - List of python types the 'args' should be.
OUTPUT: N/A, will raise exception if types are not correct.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def validate_inputs(args, types):
    assert isinstance(args, list) and isinstance(types, list)
    if len(args) != len(types):
        raise Exception(f"{inspect.stack()[0][3]} args and types len differ args:{len(args)} types:{len(types)}")
    bad_elements = []
    for idx, arg in enumerate(args):
        if type(arg) is not types[idx]:
            bad_elements.append(f"arg_num: {idx}, expected: {types[idx]}, actual: {type(arg)}")
    if len(bad_elements) != 0:
        raise Exception(f"{inspect.stack()[1][3]}: Input Validation Failed {bad_elements}")
    
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Splits up 'items' into size 'size' chunks.
INPUT: items - List of values.
       size - Chunk size we are splitting up 'items' into.
OUTPUT: Tuple of lists with given 'size'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def chunks(items: list, size: int) -> list:
    validate_inputs([items, size], [list, int])
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Generic handler for the spotify api response.
INPUT: response - Spotify api response (dictionary).
       info - List of desired info we want to pull from 'response'.
OUTPUT: List of what 'info' was pulled from 'response'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_generic_field(response: dict, info: list[str]) -> list:
    validate_inputs([response, info], [dict, list])
    ret = []
    for field in info:
        tmp_response = response
        for field_part in [field] if type(field) is not list else field:
            tmp_response = tmp_response[field_part]
        ret.append(tmp_response)
    return ret


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Returns all the 'elements' that fall within the start_date and end_date.
             Y-M is treated as Y-M-last day of month.
             Y is treated as Y-12-31.
             Any other time format will always be included.
INPUT: elements - List of elements with a ['release_date'] dictionary field.
       start_date - Datetime for start of desired selection.
       end_date - Datetime for end of desired selection.
OUTPUT: List of all 'elements' that fell within 'start_date' and 'end_date'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_elements_in_date_range(elements: list[dict], start_date: datetime, end_date: datetime) -> list[dict]:
    validate_inputs([elements, start_date, end_date], [list, datetime, datetime])
    valid_elements = []
    for element in elements:
        invalid_format_count = 0
        for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
            try:
                element_date = datetime.strptime(element["release_date"], fmt)
                if fmt == '%Y-%m':
                    element_date = element_date.replace(day=calendar.monthrange(element_date.year, element_date.month)[1])
                elif fmt == '%Y':
                    element_date = element_date.replace(day=31, month=12)

                if start_date <= element_date <= end_date:
                    valid_elements.append(element)
                    break
            except ValueError:
                invalid_format_count += 1
        if invalid_format_count >= 3:
            valid_elements.append(element)
    return valid_elements


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Scopes decorator, this will set the scopes for the function and reset them after the function is done.
INPUT: scopes_list - List of scopes to set for the function.
OUTPUT: Decorator/ wrapper which alters the scopes for the function.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def scopes(scopes_list):
    # This is the decorator that gets returned
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Set scopes before running the function
            self.spotify._scopes = scopes_list  # Use the renamed attribute
            try:
                # Execute the function with the scopes set
                return func(self, *args, **kwargs)
            finally:
                # Reset the scopes back to an empty list after function execution
                self.spotify._scopes = []  # Correctly resetting the scopes
        return wrapper
    return decorator  # Return the decorator


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Builds the field structure for the 'extract_fields' function.
INPUT: info - List of fields to extract at the base level.
       track_info - List of fields to extract at the 'track' level.
       album_info - List of fields to extract at the 'track' -> 'album' level.
       artist_info - List of fields to extract at the 'track' -> 'artists' level.
OUTPUT: Dictionary of fields to extract.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def build_field_structure(
        info: List[str] = [],
        track_info: List[str] = [],
        album_info: List[str] = [],
        artist_info: List[str] = []
    ) -> Dict[str, bool]:
    
    field_structure = {key: True for key in (info or [])}
    
    if track_info or album_info or artist_info:
        field_structure["track"] = {key: True for key in (track_info or [])}
    
    if album_info:
        field_structure["track"]["album"] = {key: True for key in album_info}
    
    if artist_info:
        field_structure["track"]["artists"] = {key: True for key in artist_info}
    
    return field_structure


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Contains the logic to find the main iterable list or single item in a Spotify API response. Currently 
             just uses a few hardcoded paths since there should only be one main iterable.
INPUT: response - Spotify api response.
       track_info - List of fields to extract at the 'track' level.
       album_info - List of fields to extract at the 'track' -> 'album' level.
       artist_info - List of fields to extract at the 'track' -> 'artists' level.
OUTPUT: Tuple of the main iterable and the path to it. (None if not found)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def find_main_iterator(response: Dict[str, Any]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    for path in [["items"], ["item"], ["playlists", "items"], ["albums", "items"], 
                 ["tracks", "items"], ["artists", "items"], ["albums"], ["artists"]]: 
        data = response
        for key in path:
            if not isinstance(data, dict) or key not in data: # If path does not exist
                break
            data = data[key]
        else:  # Successfully traversed the path
            return data, path
    return response, None


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Extracts fields from a Spotify API response. Recursively traverses the response for any sub-dictionaries.
INPUT: data - Spotify API response item or list of items.
       field_structure - Dictionary of fields to extract.
OUTPUT: List of the extracted field dictionaries.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def extract_fields(data, field_structure):
    if isinstance(data, list):
        return [extract_fields(item, field_structure) for item in data]
    elif isinstance(data, dict):
        extracted = {}
        for key, sub_structure in field_structure.items():
            if isinstance(sub_structure, bool) and sub_structure is False:
                continue
            value = data.get(key, None)  # Default to None if missing
            
            # Unwrap 'items' if it's a dictionary containing a list
            if isinstance(value, dict) and "items" in value:
                value = value["items"]
            
            if isinstance(sub_structure, dict) and isinstance(value, (dict, list)):
                extracted[key] = extract_fields(value, sub_structure)
            else:
                extracted[key] = value  # Store None if missing
        return extracted
    return data

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Abstract helper that uses spotipy. Handles are token authorization and offers abstract methods
             to better access spotify's api.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class GeneralSpotifyHelpers:
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Creates the spotipy object for the given 'username' and 'scope'.
    INPUT: scope - List of spotify scopes to request access for, note MAX_SCOPE IS ALWAYS PASSED IN.
           username - User id we use for auth and operations (requires prior authorization for scopes).
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        self._scopes = []
        self.sp = SpotipyProxy(logger=self.logger)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Generalized helper to pull specified data from a spotify api response.
    INPUT: response - Dictionary response from spotipy api call.
           field_structure - Dictionary of fields we want to pull from 'response'.
                             Follows below template
                             {<field name>: <True for pull, False for skip>, ...}
                             ex. {"name": True, "track": {"name": True, "album": {"name": True}}}.
    OUTPUT: Elements requested through the 'field_structure'.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _gather_data(self, response: Dict[str, Any], field_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = []
        while response:
            main_data, next_response_path = find_main_iterator(response)
            extracted_data = extract_fields(main_data, field_structure)
            data.extend(extracted_data if isinstance(extracted_data, list) else [extracted_data])
            
            if next_response_path and len(next_response_path) > 1:
                response = response.get(next_response_path[-2], {})
            
            response = self.sp.next(response) if "next" in response else None
        
        return data

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Validates the desired scope compared to the scopes used on the creation of the class. If the scope is 
                 out of 'scope' we throw an exception to stop us from doing something we shouldn't.
    INPUT: desired_scopes - List of desired scopes to compare against our instantiated list.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def _validate_scope(self, desired_scopes: list[str]) -> None:
        validate_inputs([desired_scopes], [list])
        
        if set(desired_scopes).intersection(set(self._scopes)) != set(desired_scopes):
            raise Exception(f"SCOPE PROTECTION: {desired_scopes} NOT IN {self._scopes}")
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # USER ════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Returns list of user's followed artists.
    INPUT: info - List of info to return from api response.
    OUTPUT: List of followed user artists with given 'info'.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_user_artists(self, info: list[str]=['id']) -> list[dict]:
        self._validate_scope(["user-follow-read"])
        
        validate_inputs([info], [list])
        return self._gather_data(
            self.sp.current_user_followed_artists(limit=50)
            ,  build_field_structure(info=info)
        )
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Returns list of user's playlists.
    INPUT: info - List of info to return from api response.
    OUTPUT: List of user's playlists with given 'info'.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_user_playlists(self, info: list[str]=['id']) -> list[dict]:
        self._validate_scope(["playlist-read-private"])
        
        validate_inputs([info], [list])
        return self._gather_data(
            self.sp.current_user_playlists(limit=50)
            , build_field_structure(info=info)
        )
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYBACK ════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Gets playback state of current spotify session.
    INPUT: track_info - List of track info we want from the track obj in the response.
           artist_info - List of artist info we want from the track obj in the response.
    OUTPUT: Returns a dict holding track, and playback information.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_playback_state(self, track_info: list[str]=['id']
                           , artist_info: list[str]=['id']) -> dict:
        self._validate_scope(["user-read-playback-state"])
        
        playback = self.sp.current_playback()
        ret = None
        
        if playback is not None and playback['item'] is not None:
            ret = {"context": None
                   , "currently_playing_type": playback['currently_playing_type']
                   , "is_playing": playback['is_playing']
                   , "shuffle_state": playback['shuffle_state']
                   , "repeat_state": playback['repeat_state']}
            
            if playback['context'] is not None:
                ret['context'] = {"type": playback['context']['type'],
                                  "id": playback['context']['uri'].split(':')[2]}
            
            # Here we have to trick our _gather_data function to think there are "multiple"
            altered_playback = playback.copy()
            altered_playback['item'] = [playback['item'].copy()]
            
            field_structure = build_field_structure(info=track_info)
            field_structure["artists"] = {key: True for key in artist_info}
            track_data = self._gather_data(playback, field_structure)
            ret['track'] = track_data[0]

        return ret
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Overwrites spotify queue with given tracks.
    INPUT: tracks - The tracks that will be written to the queue.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def write_to_queue(self, tracks: list[str]) -> None:
        self._validate_scope(["user-modify-playback-state"])
        
        for track in tracks:
            self.sp.add_to_queue(track)
            time.sleep(0.20)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Changes spotify current playback.
    INPUT: play - True if play, False if pause.
           skip - "next" if skip track, "prev" if previous track.
           shuffle - True/ False if shuffle is enabled.
           repeat - 'off', 'track', or 'context' for the state of repeat.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def change_playback(self, pause: Optional[bool]=None, 
                        skip: str="", 
                        shuffle: Optional[bool]=None, 
                        repeat: str="") -> None:
        self._validate_scope(["user-modify-playback-state"])
        
        if pause == True:
            self.sp.pause_playback()
        
        if skip == "next":
            self.sp.next_track()
        elif skip == "prev":
            self.sp.previous_track()
        
        if shuffle != None:
            self.sp.shuffle(shuffle)
        
        if repeat != "":
            self.sp.repeat(repeat)
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PLAYLISTS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Adds given tracks into the given playlist.
    INPUT: playlist_id - Id of the playlist we will add the tracks to.
           track_ids - List of track ids we will be adding to the playlist.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> None:
        self._validate_scope(["playlist-modify-public", "playlist-modify-private"])
        validate_inputs([playlist_id, track_ids], [str, list])
        
        track_chunks = chunks(track_ids, 100)
        for chunk in track_chunks:
            self.sp.playlist_add_items(playlist_id, chunk)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Adds given tracks into the given playlist BUT ONLY THE UNIQUE ONES.
    INPUT: playlist_id - Id of the playlist we will add the tracks to.
           track_ids - List of track ids we will be adding to the playlist.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def add_unique_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> None:
        self._validate_scope(["playlist-modify-public", "playlist-modify-private"])
        validate_inputs([playlist_id, track_ids], [str, list])
        
        track_ids = list(dict.fromkeys(track_ids))
        playlist_track_ids = [track['id'] for track in self.get_playlist_tracks(playlist_id)]
        tracks_to_add = [track_id for track_id in track_ids if track_id not in playlist_track_ids]
        self.add_tracks_to_playlist(playlist_id, tracks_to_add)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Grabs all the tracks with given <object>_info provided.
    INPUT: playlist_id - Id of playlist we are grabbing tracks from.
           offset - Index of the first track to grab.
           track_info - List of track info we wish to grab (defaults is 'id').
           album_info - List of album info we wish to grab (defaults is 'id').
           artist_info - List of artist info we wish to grab (defaults is 'id').
    OUTPUT: List of tracks (dict) with given info from <object>_info .
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_playlist_tracks(self, playlist_id: str, offset: int=0,
                            track_info: list[str]=['id'], 
                            album_info: list[str]=['id'], 
                            artist_info: list[str]=['id']) -> list[dict]:
        self._validate_scope(["playlist-read-private"])
        validate_inputs([playlist_id, track_info, album_info, artist_info], [str, list, list, list])
        
        res = self._gather_data(
            self.sp.playlist_items(playlist_id, limit=100, offset=offset, market="US")
            , build_field_structure(track_info=track_info, album_info=album_info, artist_info=artist_info)
        )
        return [d["track"] for d in res if "track" in d]
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Creates a new playlist for the user.
    INPUT: playlist_name - Name of the playlist that will be displayed on spotify.
           playlist_description - Description seen under name on spotify (defaults to empty).
           public - Whether the playlist is public or not.
    OUTPUT: The created playlist id (str).
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def create_playlist(self, name: str, description: str='', public: bool=False) -> str:
        self._validate_scope(["playlist-modify-public", "playlist-modify-private"])
        if len(self.get_user_playlists()) >= 400:
            raise Exception(f"User has more than 400 playlists, skipping creation")
        validate_inputs([name, description, public], [str, str, bool])
        
        return self.sp.user_playlist_create(os.getenv("CLIENT_USERNAME"), name, description=description, 
                                            public=public)['id']
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Changes given playlists description or name.
    INPUT: playlist_id - Id of playlist we will change the description/ name of.
           name - Name we will use to overwrite the current playlist name.
           description - Description we will use to overwrite the current description.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def change_playlist_details(self, playlist_id: str, 
                                name: Optional[str]=None, 
                                description: Optional[str]=None):
        self._validate_scope(["playlist-modify-public", "playlist-modify-private"])
        validate_inputs([playlist_id], [str])
        
        if name is not None and description is not None:
            self.sp.playlist_change_details(playlist_id, name=name, description=description)
        elif name is not None:
            self.sp.playlist_change_details(playlist_id, name=name)
        elif description is not None:
            self.sp.playlist_change_details(playlist_id, description=description)
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    DESCRIPTION: Removes all tracks from a playlist assuming it is in our PLAYLISTS_WE_CAN_DELETE_FROM list.
    INPUT: playlist_id - Id of playlist we will delete all tracks from.
           max_playlist_length - Second gate to always check how many tracks we "expect" to delete.
    OUTPUT: Bool on whether or not it successfully removed the tracks.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def remove_all_playlist_tracks(self, playlist_id: str, max_playlist_length: int=0):
        self._validate_scope(["playlist-modify-public", "playlist-modify-private", Settings.DELETE_SCOPE])
        tracks = []
        if playlist_id in Settings.PLAYLISTS_WE_CAN_DELETE_FROM:
            tracks = self.get_playlist_tracks(playlist_id)
            if len(tracks) <= max_playlist_length:
                for chunk in chunks([track['id'] for track in tracks], 60):
                    self.sp.playlist_remove_all_occurrences_of_items(playlist_id, chunk)
                return True
        
        self.logger.error(f"Incorrectly Called DELETE With Playlist: ID: {playlist_id}, " +
                                   f"Length: {len(tracks)}, Max: {max_playlist_length}")
        return False
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ARTISTS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Grabs all the given artists albums of type 'album_type' and returns 'info' on that album.
    INPUT: artist_id - Id of the artist we will be grabbing albums from.
           album_types - Type of albums we are requesting. Types are  album, single, appears_on, and compilation.
           info - Info we will grab for the albums can be id, name, and release_date. 
                              There are more but I know those work.
    OUTPUT: List of album dictionaries with 'info' for the given artist.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_artist_albums(self, artist_id:str, 
                          album_types: list[str]=['album'], 
                          info: list[str]=['id']):
        validate_inputs([artist_id, album_types, info], [str, list, list])
        
        return self._gather_data(
            self.sp.artist_albums(artist_id
                                  , country="US"
                                  , limit=50
                                  , include_groups=','.join(album_types))
            , build_field_structure(info=info)
        )


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Get all album, single, and appears_on tracks by the given artist between the start_date and end_date
                 if no start or end date is given no filtering will be done.
    INPUT: artist_id - Id of the artist we will be grabbing tracks from.
           start_date - Datetime of the start of our range.
           end_date - Datetime of the end of our range.
    OUTPUT: List of track id's from the given artist. The albums/ singles are first and ordered in chronological 
            order, the appears_on tracks are simply added on to the end.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def gather_tracks_by_artist(self, artist_id:str, 
                                start_date: Optional[datetime]=None, 
                                end_date: Optional[datetime]=None) -> list[str]:
        # validate_inputs([artist_id, start_date, end_date], [str, datetime, datetime])
        
        # Gather all artists albums/ singles
        artist_albums = self.get_artist_albums(artist_id
                                                , album_types=['album', 'single']
                                                , info=['id', 'release_date', 'album_type'])
        # Remove all compilations
        artist_albums = [album for album in artist_albums if album['album_type'] != 'compilation']
        
        # Sort albums by release date
        artist_albums.sort(key=lambda x: x['release_date'])
        
        # Grab those only within our date range
        if start_date is not None and end_date is not None:
            artist_albums = get_elements_in_date_range(artist_albums, start_date, end_date)

        # Gather the tracks from these albums
        album_tracks = [track["id"] for album in 
                        self.get_albums_tracks([album['id'] for album in artist_albums]) for track in album['tracks']]

        # Gather all albums/ singles artist appeared on
        artist_appears_on_albums = self.get_artist_albums(artist_id
                                                , album_types=['appears_on']
                                                , info=['id', 'release_date', 'album_type'])

        # Remove all compilations
        artist_appears_on_albums = [album for album in artist_appears_on_albums 
                                    if album['album_type'] != 'compilation']
        # Grab those only within our date range
        if start_date is not None and end_date is not None:
            artist_appears_on_albums = get_elements_in_date_range(artist_appears_on_albums, start_date, end_date)
        # Gather the tracks from these albums
        appears_on_album_tracks = self.get_albums_tracks([album['id'] for album in artist_appears_on_albums]
                                                         , album_info=['id', 'release_date']
                                                         , track_info=['id', 'name'])
        # Get only the tracks that our artist supported
        appears_on_album_tracks = [track for album in appears_on_album_tracks for track in album['tracks'] 
                                   for artist in track['artists'] if artist_id in artist.values()]
        # Validate each track in this list
        appears_on_album_tracks = self.verify_appears_on_tracks(appears_on_album_tracks, artist_id)

        return album_tracks + appears_on_album_tracks

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ALBUMS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Gathers all of an albums tracks and returns with given <object>_info info.
                 info can be id, name, and release_date. There are more but I know those work.
    INPUT: album_ids - List of spotify scopes to request access for.
           album_info - List of info we wish to grab for the given album.
           track_info - List of info we wish to grab from each track in the album.
           artist_info - List of info we wish to grab from the artists for each of the tracks.
    OUTPUT: List of track dicts containing the requested info.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_albums_tracks(self, album_ids: list[str], 
                          album_info:  list[str]=['id'], 
                          track_info:  list[str]=['id'], 
                          artist_info: list[str]=['id']) -> list[dict]:
        validate_inputs([album_ids, album_info, track_info], [list, list, list])
        
        album_chunks = chunks(album_ids, 20)
        field_structure = {key: True for key in album_info}
        field_structure["tracks"] = {key: True for key in track_info}
        field_structure["tracks"]["artists"] = {key: True for key in artist_info}

        return [album for album_chunk in album_chunks
                for album in self._gather_data(self.sp.albums(album_chunk, market="US"), field_structure)]

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACKS ══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Gets all artists from the given track .
    INPUT: track_id - List of spotify scopes to request access for.
    OUTPUT: List of artist ids for the given track.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_track_artists(self, track_id: str, info: list[str]=['id']) -> list[str]:
        validate_inputs([track_id], [str])
        
        artist_ids = []
        for artist_data in self.sp.track(track_id, market="US")['artists']:
            data = []
            for elem in info:
                data.append(artist_data[elem])
            artist_ids.append(data)
        return artist_ids

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Verifies if the given track is the "unique" one just by searching for it, if it's the first 
                 result then it is unique, if not then it's probably a duplicate.
    INPUT: tracks - List of spotify tracks we will be verifying.
           artist_id - Str of the given artist so we can better tell if it's theirs.
    OUTPUT: List of the tracks we have verified.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def verify_appears_on_tracks(self, tracks: list[str], artist_id: str) -> list[str]:
        validate_inputs([tracks, artist_id], [list, str])
        
        valid_tracks = []
        for track in tracks:
            artist_name = self.get_artist_data(track['artists'][0]['id'], ['name'])[0]
            track_name = ''.join(e for e in track['name'] if e.isalnum() or e == " ")
            tracks_data = self.sp.search(f"{track_name}%20artist:{artist_name}", 
                                         limit=5, type='track', market="US")['tracks']['items']
            for track_data in tracks_data:
                track_id = track_data['id']
                if track_id == track['id']:
                    valid_tracks.append(track['id'])
                    break

            if len(tracks_data) == 0:
                valid_tracks.append(track['id'])
        return valid_tracks

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # MISC HELPERS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Simple getters to take a given track, artist, album, or playlist id and return requested fields.
    INPUT: <input>_id - Str id of spotify object.
           info - Desired info we want from the spotify response (returns 'id' if not specified).
    OUTPUT: List of what 'info' we got from the given <input>_id.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_track_data(self, track_id: str, info: list[str]=['id']) -> list[str]:
        validate_inputs([track_id, info], [str, list])
        return get_generic_field(self.sp.track(track_id, market="US"), info)

    def get_artist_data(self, artist_id: str, info: list[str]=['id']) -> list[str]:
        validate_inputs([artist_id, info], [str, list])
        return get_generic_field(self.sp.artist(artist_id), info)

    def get_album_data(self, album_id: str, info: list[str]=['id']) -> list[str]:
        validate_inputs([album_id, info], [str, list])
        return get_generic_field(self.sp.album(album_id, market="US"), info)

    def get_playlist_data(self, playlist_id: str, info: list[str]=['id']) -> list[str]:
        validate_inputs([playlist_id, info], [str, list])
        return get_generic_field(self.sp.playlist(playlist_id, market="US"), info)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════