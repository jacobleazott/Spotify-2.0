# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    MISC FEATURES                            CREATED: 2024-09-22          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file contains simple misc features. Only features that can be comfortably done in one function should be in
#   this file. If it requires anything additional it should receive its own dedicated file.
#
# Current Features:
#   generate_artist_release - Takes given artist_id(s), playlist name, playlist desc, start/ end date, and creates a 
#                               new playlist with all the tracks from those artists released within the given dates.
# 
#   distribute_tracks_to_collections_from_playlist - Takes an id of a playlist and distributes the tracks within to all
#                                                      of our 'artist' playlists as well as 'Master' and 'Year'.
# 
#   reorganize_playlist - Sorts a playlist by release date and track number. Does not delete but adds to the end.
# 
#   update_daily_latest_playlist - Creates a playlist of our 'latest' tracks we have added to our collections. Deletes
#                                    tracks. 'LATEST_PLAYLIST_LENGTH' determines number of tracks.
# 
#   generate_featured_artists_list - Generates a list of all contributing artists from our collection that we do not 
#                                      currently follow. Attached data is how many tracks they appear on and how many
#                                      unique artists they collaborate with in our followed artists.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
from datetime import datetime
from collections import defaultdict

import src.General_Spotify_Helpers as gsh
from src.helpers.decorators import *
from src.helpers.Database_Helpers import DatabaseHelpers
from src.helpers.Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MiscFeatures(LogAllMethods):
        
    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Returns the first artist of the first track out of a playlist (not from our macro list).
    INPUT: playlist_id - Id of playlist we will grab artist_id from.
    OUTPUT: Str of the first artist of the first non macro track.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_first_artist_from_playlist(self, playlist_id: str) -> str:
        playlist_tracks = self.spotify.get_playlist_tracks(playlist_id, artist_info=['id', 'name'])
        return [track for track in playlist_tracks if track['id'] not in Settings.MACRO_LIST][0]['artists'][0]['id']

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Generates a new playlist of released tracks within the given date range for the given artists.
    INPUT: artist_id_list - List of spotify artist_id's we want to gather tracks from.
           playlist_name - Name that the new playlist will be given.
           playlist_description - Description that the new playlist will be given.
           start_date - Start day of track collection.
           end_date - End day of track collection.
           logger - Logger object used.
    OUTPUT: Str of playlist_id created.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def generate_artist_release(self, artist_id_list: list[str], playlist_name: str, playlist_description: str,
                start_date: Optional[datetime]=None, end_date: Optional[datetime]=None) -> str:
        playlist_id = self.spotify.create_playlist(playlist_name, description=playlist_description)
        self.logger.info(f"Created New Playlist: {playlist_id}")
        
        tracks = []
        for artist_id in artist_id_list:
            self.logger.info(f"finding tracks for {artist_id}")
            tmp_tracks = self.spotify.gather_tracks_by_artist(artist_id, 
                                                          start_date=start_date, 
                                                          end_date=end_date)
            self.logger.info(f"\tFound {len(tmp_tracks)} tracks")
            tracks += tmp_tracks
            
        self.logger.info(f"Adding {len(tracks)} tracks to playlist {playlist_id}")
        self.logger.debug(f"Tracks: {tracks}")
        self.spotify.add_tracks_to_playlist(playlist_id, tracks)
        
        return playlist_id
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Distributes tracks from given playlist into their respective 'good', 'year', and 'artist' playlists.
    INPUT: playlist_id - Id of playlist we will grab tracks from to distribute to our collections.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def distribute_tracks_to_collections_from_playlist(self, playlist_id: str) -> None:
        user_playlists = self.spotify.get_user_playlists(info=['id', 'name'])
        good_playlist = None
        year_playlist = None
        artist_playlists = list()
        
        for playlist in user_playlists:
                if playlist["id"] == Settings.MASTER_MIX_ID:
                    good_playlist = playlist
                    
                if playlist["name"].startswith(str(datetime.today().year)):
                    year_playlist = playlist
                
                if playlist["name"].startswith('__'):
                    playlist["tracks"] = []
                    artist_playlists.append(playlist)
                    
        if good_playlist is None or year_playlist is None or len(artist_playlists) == 0:
            raise Exception(f"Missing Integral Playlists The Good: {good_playlist} Year: {year_playlist} \
                            Artists: {len(artist_playlists)}")
        
        self.logger.info(f"Found {len(artist_playlists)} Artist Playlists. Grabbing Playlist - {playlist_id}")
        
        tracks_to_distribute = self.spotify.get_playlist_tracks(playlist_id, track_info=['id', 'name'], 
                                                                artist_info=['id', 'name'])
        
        self.logger.info(f"Found {len(tracks_to_distribute)} Tracks")
        self.logger.debug(f"Tracks: {tracks_to_distribute}")
        
        # Add all tracks we need to distribute to their respective artist track holder
        for track in tracks_to_distribute:
            self.logger.info(f"Track - {track['name']}, {track['id']}")
            verified = False
            for playlist_artist in artist_playlists:
                for track_artist in track['artists']:
                    if track_artist['name'] == playlist_artist['name'][2:]:
                        playlist_artist['tracks'].append(track['id'])
                        verified = True
                        self.logger.info(f"\t\tArtist: {track_artist['name']}, {track_artist['id']}")
            if not verified:
                self.logger.error("NO CONTRIBUTING ARTIST FOUND")
                        
        # Distribute all the track holders to their respective artist
        tracks_to_add_to_big_playlists = []
        for playlist in artist_playlists:
            if len(playlist['tracks']) > 0:
                self.logger.info(f"Adding {len(playlist['tracks'])} to Playlist - {playlist['name']}, \
                         Tracks: {playlist['tracks']}")
                self.spotify.add_unique_tracks_to_playlist(playlist["id"], playlist['tracks'])
                tracks_to_add_to_big_playlists += playlist['tracks']
                
        self.logger.info(f"Adding {len(tracks_to_add_to_big_playlists)} To \"The Good\" and {datetime.today().year}")
        self.logger.debug(f"Tracks: {tracks_to_add_to_big_playlists}")
        
        self.spotify.add_unique_tracks_to_playlist(good_playlist["id"], tracks_to_add_to_big_playlists)
        self.spotify.add_unique_tracks_to_playlist(year_playlist["id"], tracks_to_add_to_big_playlists)
        
        self.logger.info(f"Finished Adding Tracks To \"The Good\" and year {datetime.today().year}")
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: This takes all non-local tracks and organizes them. It then adds the tracks back into the playlist 
                 at the bottom so we never mess with deleting tracks. The tracks are ordered by release date and then
                 ordered by album/ disc number/ track number.
    INPUT: playlist_id - Id of playlist we are going to "reorganize".
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def reorganize_playlist(self, playlist_id):
        tracks = self.spotify.get_playlist_tracks(playlist_id, 
                                                track_info=['id', 'name', 'disc_number', 'track_number', 'is_local'],
                                                album_info=['release_date', 'id'])
        
        self.logger.info(f"Found {len(tracks)} Tracks To Distribute. Tracks Unorganized: {tracks}")

        album_sorted_dict = {}
        for track in tracks:
            del track['artists']
            if track['is_local']:
                continue
            elif track['album_id'] not in album_sorted_dict:
                album_sorted_dict[track['album_id']] = []
            album_sorted_dict[track['album_id']].append(track)
            
        # Within each album sort by disc number / track number
        album_track_sorted_list = []
        for key, value in album_sorted_dict.items():
            tmp_tracks = sorted(value, key=lambda element: (element['disc_number'], element['track_number']))
            album_track_sorted_list.append((tmp_tracks[0]['album_release_date'], 
                                            [track['id'] for track in tmp_tracks]))

        # Order collection by release date
        album_track_sorted_list.sort()
        
        # Collapse it all into just a list of id's
        track_ids_ordered = []
        for album in album_track_sorted_list:
            track_ids_ordered += album[1]
            
        self.logger.info(f"Organized {len(track_ids_ordered)} Tracks, {tracks}")
        if len(track_ids_ordered) != len(tracks):
            raise exception("TRACK LIST MISMATCH IN DISTRIBUTION")
            
        # Remove any MACROS present in list
        for macro in Settings.MACRO_LIST:
            try:
                track_ids_ordered.remove(macro)
            except ValueError:
                pass
        
        self.spotify.add_tracks_to_playlist(playlist_id, track_ids_ordered)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs the latest 'PLAYLIST_LENGTH' tracks from 'SOURCE_PLAYLIST' and adds them to our 'DEST_PLAYLIST'
                 playlist after emptying it.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def update_daily_latest_playlist(self):
        # Grab # of tracks, subtracts PLAYLIST_LENGTH so we will always grab the right amount.
        tracks = [Settings.SHUFFLE_MACRO_ID]
        offset = self.spotify.get_playlist_data(Settings.LATEST_SOURCE_PLAYLIST, info=[['tracks', 'total']])[0] \
                    - Settings.LATEST_PLAYLIST_LENGTH
        tracks += [track['id'] for track in self.spotify.get_playlist_tracks(Settings.LATEST_SOURCE_PLAYLIST, 
                                                                             offset=offset)]
        
        remove_success = self.spotify.remove_all_playlist_tracks(Settings.LATEST_DEST_PLAYLIST, 
                                                                 max_playlist_length=Settings.LATEST_PLAYLIST_LENGTH+1)
        if remove_success:
            self.spotify.add_tracks_to_playlist(Settings.LATEST_DEST_PLAYLIST, tracks)
            
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a list of all artists that appear in our 'Master' collection that we do not follow.
                 This list is ordered first by # of unique artists we follow that they appear with followed by total
                 number of tracks they appear on.
    INPUT: min_featured_tracks (optional) - Minimum number of tracks before adding as a featured artist.
    OUTPUT: List of our featured artists that we do not follow sorted.
            {<artist_id>: (<artist_name>, <num_tracks_appeared_on>, <followed_artists>, <tracks_appeared_on>),}
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_featured_artists_list(self, min_featured_tracks: int = 1) -> list:
        tracks_to_ignore = set()
        dbh = DatabaseHelpers(logger=self.logger)
        artist_ids = {artist['id'] for artist in dbh.db_get_user_followed_artists()}
        playlist_tracks = dbh.db_get_tracks_from_playlist(Settings.MASTER_MIX_ID)

        for ignored_artist in Settings.PLAYLIST_IDS_NOT_IN_ARTISTS:
            tracks_to_ignore.update(track['id'] for track in dbh.db_get_tracks_from_playlist(ignored_artist))

        # (artist_name, num_tracks, unique_artists, track_names)
        artist_data = defaultdict(lambda: ["", 0, set(), []])  

        for track in playlist_tracks:
            tmp_following_artists, tmp_new_artists = [], []
            if track['id'] in tracks_to_ignore or track['is_local']:
                continue

            for artist in dbh.db_get_track_artists(track['id']):
                if artist['id'] in artist_ids:
                    tmp_following_artists.append((artist['id'], artist['name']))
                else:
                    tmp_new_artists.append((artist['id'], artist['name']))

            for artist_id, artist_name in tmp_new_artists:
                artist_entry = artist_data[artist_id]
                artist_entry[0] = artist_name                   # Store artist name
                artist_entry[1] += 1                            # Increment track count
                artist_entry[2].update(tmp_following_artists)   # Update unique artists set
                artist_entry[3].append(track['name'])           # Store track names

        # Sort by unique artist count (len(item[1][2])) then by num_tracks (item[1][1])
        return sorted(artist_data.items(), key=lambda item: (len(item[1][2]), item[1][1]), reverse=True)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════