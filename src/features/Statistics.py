# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    STATISTICS                               CREATED: 2025-03-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Various functions that generate statistics about the Spotify data we have. 
#
#  generate_featured_artists_list - Generates a list of all contributing artists from our collection that we do not 
#                                      currently follow. Attached data is how many tracks they appear on and how many
#                                      unique artists they collaborate with in our followed artists.
#
#  generate_latest_artists - Generates a list of artists that we have listened to the most in the last specified time
#                               period. It sorts in descending order by total minutes listened.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import sqlite3
from datetime import datetime

from src.helpers.decorators       import *
from src.helpers.Settings         import Settings
from src.helpers.Database_Helpers import DatabaseHelpers

class SpotifyStatistics(LogAllMethods):
    
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else logging.getLogger()
        self.dbh = DatabaseHelpers(logger=self.logger)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a list of all artists that appear in our 'Master' collection that we do not follow.
                 This list is ordered first by # of unique artists we follow that they appear with followed by total
                 number of tracks they appear on.
    INPUT: num_artists - Number of artists to return.
    OUTPUT: List of our featured artists that we do not follow sorted.
            {<artist_id>: (<artist_name>, <num_tracks_appeared_on>, <followed_artists>, <tracks_appeared_on>),}
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def generate_featured_artists_list(self, num_artists: int) -> list:
        tracks_to_ignore = set()
        artist_ids = {artist['id'] for artist in self.dbh.db_get_user_followed_artists()}
        
        for ignored_artist in Settings.PLAYLIST_IDS_NOT_IN_ARTISTS:
            tracks_to_ignore.update(track['id'] for track in self.dbh.db_get_tracks_from_playlist(ignored_artist))
        
        playlist_tracks = [track for track in self.dbh.db_get_tracks_from_playlist(Settings.MASTER_MIX_ID) 
                            if track['id'] not in tracks_to_ignore and not track['is_local']]

        artist_data = {}

        for track in playlist_tracks:
            tmp_following_artists, tmp_new_artists = [], []

            for artist in self.dbh.db_get_track_artists(track['id']):
                if artist['id'] in artist_ids:
                    tmp_following_artists.append(artist['name'])
                else:
                    tmp_new_artists.append((artist['id'], artist['name']))

            for artist_id, artist_name in tmp_new_artists:
                if artist_id not in artist_data:
                    artist_data[artist_id] = {'Artist Name': artist_name
                                            , 'Number of Tracks': 1
                                            , 'Unique Artists': set(tmp_following_artists)
                                            , 'Track Names': [track['name']]}
                else:
                    artist_data[artist_id]['Number of Tracks'] += 1
                    artist_data[artist_id]['Unique Artists'].update(tmp_following_artists)
                    artist_data[artist_id]['Track Names'].append(track['name'])
                    
        sorted_list = sorted(artist_data.items(), key=lambda artist: 
            (artist[1]['Number of Tracks'] + 2 * len(artist[1]['Unique Artists'])), reverse=True)
        
        # Convert sets to lists
        for artist_id, artist_data in sorted_list:
            artist_data['Unique Artists'] = list(artist_data['Unique Artists'])
        
        return [artist[1] for artist in sorted_list[:num_artists]]
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a list of the artists that we have listened to the most in the last specified time period.
    INPUT: start_date - The start date of the time period we want to generate the list for.
           end_date   - The end date of the time period we want to generate the list for.
           num_artists - Number of artists to return.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # TODO: BRO-131 Fix so we can allow a query spanning multiple years
    # TODO We probably need to track tracks not found in the database, this would be fixed by the smart interface... But we are
    #       losing track data here if we don't have the tracks saved, or the playlists were once and then got deleted like GO THROUGH
    def generate_latest_artists(self, start_date, end_date=datetime.now(), num_artists=5):
        with sqlite3.connect(Settings.LISTENING_DB) as ldb_conn:
            # Fetch relevant track_ids from ldb_conn within the date range
            track_query = f"""
                SELECT track_id, COUNT(*) as track_count
                FROM '{datetime.now().year}'
                WHERE time BETWEEN ? AND ?
                GROUP BY track_id;
            """
            track_cursor = ldb_conn.execute(track_query, (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))
            track_counts = track_cursor.fetchall()

            if not track_counts:
                return []

            # Create a mapping of track_id to count
            track_id_to_count = {track_id: count for track_id, count in track_counts}

            # Get all matching track_ids
            track_ids = list(track_id_to_count.keys())

            # Get artist information and calculate listening time
            artist_query = f"""
                SELECT ta.id_artist, a.name, t.id
                FROM tracks t
                JOIN tracks_artists ta ON t.id = ta.id_track
                JOIN artists a ON ta.id_artist = a.id
                WHERE t.id IN ({','.join('?' for _ in track_ids)});
            """
            artist_data = self.dbh.backup_db_conn.execute(artist_query, track_ids).fetchall()

            # Aggregate listening time by artist
            artist_listening_time = {}
            for artist_id, artist_name, track_id in artist_data:
                if artist_id not in artist_listening_time:
                    artist_listening_time[artist_id] = [artist_name, 0]
                artist_listening_time[artist_id][1] += track_id_to_count[track_id] * 15

            # Sort artists by listening time
            top_artists = sorted(artist_listening_time.values(), key=lambda x: x[1], reverse=True)[:num_artists]

            return [{'Artist': artist[0], 'Listening Time (min)': artist[1]/60} for artist in top_artists]


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════