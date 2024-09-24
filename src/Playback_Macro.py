# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    PLAYBACK MACRO HANDLER                  CREATED: 2021-07-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This script records the current playback of the user into a listening_db. In addition it handles any macros we wish
#   to use. Currently those macros are if you play the song 'Medidation' (which is just elevator music) and depending
#   on your shuffle state it will either queue up a weighted random or 'pure' random selection. The weighted random
#   is based off of the amount of times you have listened to a track in an effort to fight against spotify playing
#   the same 4 songs over and over again. 
#
# For a track to count as being "listened" to for the listening_data db and the track_counts (used for the weighted
#   random). You must to have called this script twice and the same song is still playing. (Stored between runs in
#   a pickle file). I run this track every 15s and so that means you need to listen to the song for 15-30s (depending 
#   on timing from track start and macro start) for it to count towards being "listened"
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import General_Spotify_Helpers as gsh
import logging as log
import datetime
import sqlite3
import pickle
import time
import random

SCOPE = ["user-read-playback-state"
        , "user-modify-playback-state"
        , "playlist-read-private"
        , "playlist-read-collaborative"
        , "playlist-modify-public"
        , "playlist-modify-private"]

QUEUE_LENGTH = 80
PICKLE_FILENAME = "databases/lastTrack.pk"
LISTENING_DB = "databases/listening_data.db"
TRACK_COUNTS_DB = "databases/track_counts.db"

spotify = gsh.GeneralSpotifyHelpers(SCOPE)

# We grab datetime here because filling the queue can take a little bit of time and we want time to be accurate
# This needs to be fixed, it assumes a mod 30 with 30s increments, but we use 15s increments now so probably need a little more
dt = (datetime.datetime.now() - datetime.timedelta(
    seconds=int(datetime.datetime.now().strftime(r"%S")))).strftime(r"%Y-%m-%d %H:%M:%S")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Either adds the new track to our track_count db or increments it by 1
INPUT: track_id - id of track we are updating
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Increments the track_counts.db for the given track_id or adds it to the db
def increment_play_count_db(track_id):
    track_counts_conn = sqlite3.connect(TRACK_COUNTS_DB)
    track_counts_conn.execute(f'''CREATE TABLE IF NOT EXISTS 'tracks'(
         track_id TEXT PRIMARY KEY,
         play_count INTEGER NOT NULL);''')

    # Checks ot see if the track is already in the database or not
    if not bool(track_counts_conn.execute(
            f"SELECT COUNT(*) from 'tracks' WHERE 'tracks'.track_id = '{track_id}'").fetchone()[0]):
        track_counts_conn.execute(f"""INSERT INTO 'tracks'
                          ('track_id', 'play_count') 
                          VALUES (?, ?);""", (track_id, 1))
    else:
        track_counts_conn.execute(f"""UPDATE 'tracks'
                            SET play_count = play_count + 1 
                            WHERE track_id = '{track_id}'""")

    track_counts_conn.commit()
    track_counts_conn.close()


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Reads our pickle file to determine if we have listened to the track for at least 30s and updates as
             necessary
INPUT: track_id - what id we are currently listening to
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def update_last_track_count(track_id):
    try:
        with open(PICKLE_FILENAME, 'rb') as fi:
            last_track_pickle = pickle.load(fi)
    except EOFError:
        last_track_pickle = "", False

    if last_track_pickle is None or last_track_pickle[0] != track_id:
        with open(PICKLE_FILENAME, 'wb') as fi:
            pickle.dump((track_id, True), fi)
    else:
        if last_track_pickle[1]:
            with open(PICKLE_FILENAME, 'wb') as fi:
                pickle.dump((track_id, False), fi)
            increment_play_count_db(track_id)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Logs the current playing track into our listening.db
INPUT: track_id - id of the track we are currently listening to
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def log_track(track_id):
    year = datetime.datetime.now().year
    conn = sqlite3.connect(LISTENING_DB)

    conn.execute(f'''CREATE TABLE IF NOT EXISTS '{year}'(
            track_id TEXT NOT NULL,
            time timestamp NOT NULL);''')

    conn.execute(f"""INSERT INTO '{year}' ('track_id', 'time') 
                     VALUES ("{track_id}", "{dt}");""")
    conn.commit()
    conn.close()

    update_last_track_count(track_id)
    
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates a weighted queue for listening, it orders tracks from least to most listened and 'partially'
             randomizes the queue based upon how many times specifically we have listened to each track
INPUT: track_ids - list of tracks we pulled from the playlist and are making the weighted queue off of
OUTPUT: list of tracks partially randomized in the reverse weighted form
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def make_weighted(track_ids):
    track_counts_conn = sqlite3.connect(TRACK_COUNTS_DB)
    track_count_data = []

    # Grab all the track_counts for our track_ids, we default to 0 listens if we don't find it
    for track_id in track_ids:
        if track_id == gsh.SHUFFLE_MACRO_ID:
            continue
        track_query = track_counts_conn.execute(f"SELECT * FROM 'tracks' WHERE 'tracks'.track_id = '{track_id}'").fetchone()

        if track_query is None:
            track_count_data.append((0, track_id))
        else:
            track_count_data.append((track_query[1], track_id))
    
    track_counts_conn.close()
    track_count_data.sort()
  
    # Below we are going to group same play_count tracks, so we start with [[1, a], [1, b], [4, c], [4, d], [5, e]]
    #   and end with [[a, b], [c, d], [e]]. Once we reach a minimum of QUEUE_LENGTH of total tracks in 
    #   track_count_groupings we exit out since we don't care past that
    tmp_play_count = 0
    tmp_track_count_group = []
    track_count_groupings = []

    for idx, track in enumerate(track_count_data):
        if track[0] > tmp_play_count and len(tmp_track_count_group) > 0:
            track_count_groupings.append(tmp_track_count_group)
            tmp_play_count = track[0]
            tmp_track_count_group = []
            if idx >= QUEUE_LENGTH:
                break
        tmp_track_count_group.append(track[1])
    track_count_groupings.append(tmp_track_count_group)
        
    # Now we randomize each "set" of track_counts individually and add them up to one master list
    track_list = []
    random.seed(datetime.datetime.now().timestamp())
   
    for track_group in track_count_groupings:
        random.shuffle(track_group)
        track_list += track_group
    
    return track_list[:min(len(track_list), QUEUE_LENGTH)]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Handles the shuffle macro, whether it is a weighted shuffle or random based upon shuffle state
INPUT: shuffle_state - whether shuffle is turned on our not
       playlist_id - id of playlist we are shuffling/ currently playing
OUTPUT: track_id the "next" track that we are playing
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def shuffle_macro(shuffle_state, playlist_id):
    gsh.validate_inputs([shuffle_state, playlist_id], [bool, str])
    
    spotify.change_playback(skip="next", shuffle=True)
    
    track_id = spotify.get_playback_state()[0]
    tracks = [track['id'] for track in spotify.get_playlist_tracks(playlist_id) if track['id'] is not None]
    # If shuffle_state is true it's a weighted queue, if it is false it is 'pure' random
    if shuffle_state:
        tracks = make_weighted(tracks)
    else:
        random.seed(datetime.datetime.now().timestamp())
        random.shuffle(tracks)

    if gsh.SHUFFLE_MACRO_ID in tracks:
        tracks.remove(gsh.SHUFFLE_MACRO_ID)

    tracks = tracks[:(min(len(tracks), QUEUE_LENGTH))]
    spotify.write_to_queue(tracks)
    
    return track_id


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Generates a playlist of an artists entire discography, must be playing the GEN_ARTIST_MACRO_ID song
             in a brand new playlist named "My Playlist #" followed by digits. The only other track in the playlist 
             should be a single artist track of the artist we want to create the playlist for
INPUT: playlist_id - playlist we will change to artist GO THROUGH playlist (NOTE THIS REMOVES ALL TRACKS up to 2)
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_artist_playlist_macro(playlist_id):
    gsh.validate_inputs([playlist_id], [str])
    
    playlist_tracks = spotify.get_playlist_tracks(playlist_id, artist_info=['id', 'name'])
    
    if len(playlist_tracks) < 2:
        return
    
    track = [track for track in playlist_tracks if track['id'] != gsh.GEN_ARTIST_MACRO_ID][0]
    
    artist_tracks = spotify.gather_tracks_by_artist(track['artists'][0]['id'])
    spotify.change_playlist_details(playlist_id, 
                                    name=f"{track['artists'][0]['name']} GO THROUGH", 
                                    description=f"All the tracks from {track['artists'][0]['name']}")
    spotify.remove_all_playlist_tracks(playlist_id, max_playlist_length=2)
    spotify.add_tracks_to_playlist(playlist_id, artist_tracks)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Distributes tracks from currently playing playlist into their respective good, year, and artist playlist
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def distribute_tracks_to_playlists(playlist_id):
    gsh.validate_inputs([playlist_id], [str])
    
    log.basicConfig(filename=f'logs/Distribute-{datetime.datetime.date(datetime.datetime.today())}.log', level=log.INFO, filemode='a',
                format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S')
    
    user_playlists = spotify.get_user_playlists(info=['id', 'name'])
    good_playlist = None
    year_playlist = None
    artist_playlists = list()
    
    for playlist in user_playlists:
            if playlist["name"].startswith('The Good - Master Mix'):
                good_playlist = playlist
                
            if playlist["name"].startswith(str(datetime.datetime.today().year)):
                year_playlist = playlist
            
            if playlist["name"].startswith('__'):
                playlist["tracks"] = []
                artist_playlists.append(playlist)
                
    if good_playlist is None or year_playlist is None or len(artist_playlists) == 0:
        error_str = f"Missing Integral Playlists The Good: {good_playlist} Year: {year_playlist} Artists: {len(artist_playlists)}"
        log.error(error_str)
        raise Exception(error_str)
    
    log.info(f"Found {len(artist_playlists)} Artist Playlists")

    log.info(f"Grabbing Tracks From Playlist - {playlist_id}")
    tracks_to_distribute = spotify.get_playlist_tracks(playlist_id, track_info=['id', 'name'], artist_info=['id', 'name'])
    log.info(f"Found {len(tracks_to_distribute)} Tracks")
    log.debug(f"Tracks: {tracks_to_distribute}")
    
    for track in tracks_to_distribute:
        log.info(f"Track - {track['name']}, {track['id']}")
        for playlist_artist in artist_playlists:
            for track_artist in track['artists']:
                if track_artist['name'] == playlist_artist['name'][2:]:
                    playlist_artist['tracks'].append(track['id'])
                    log.info(f"\t\tArtist: {track_artist['name']}, {track_artist['id']}")
                    
    tracks_to_add_to_big_playlists = []
    for playlist in artist_playlists:
        if len(playlist['tracks']) > 0:
            log.info(f"Adding {len(playlist['tracks'])} to Playlist - {playlist['name']}")
            log.debug(f"Tracks: {playlist['tracks']}")
            spotify.add_unique_tracks_to_playlist(playlist["id"], playlist['tracks'])
            tracks_to_add_to_big_playlists += playlist['tracks']
            
    log.info(f"Adding {len(tracks_to_add_to_big_playlists)} To \"The Good\" and {datetime.datetime.today().year}")
    log.debug(f"Tracks: {tracks_to_add_to_big_playlists}")
    spotify.add_unique_tracks_to_playlist(good_playlist["id"], tracks_to_add_to_big_playlists)
    spotify.add_unique_tracks_to_playlist(year_playlist["id"], tracks_to_add_to_big_playlists)
    log.info(f"Finished Adding Tracks To \"The Good\" and year {datetime.datetime.today().year}")
    
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: This macro takes all non-local tracks and organizes them. It then adds the tracks back into the playlist
             at the bottom so we never mess with deleting tracks. The tracks are ordered by release date and then
             ordered by album/ disc number/ track number.
INPUT: playlist_id - id of playlist we are going to "reorganize"
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def reorganize_playlist(playlist_id):
    tracks = spotify.get_playlist_tracks(playlist_id, 
                                        track_info=['id', 'name', 'disc_number', 'track_number', 'is_local'],
                                        album_info=['release_date', 'id'])

    album_sorted_dict = {"local_tracks": []}
    for track in tracks:
        del track['artists']
        if track['is_local']:
            album_sorted_dict['local_tracks'].append(track)
            continue
        elif track['album_id'] not in album_sorted_dict:
            album_sorted_dict[track['album_id']] = []
        album_sorted_dict[track['album_id']].append(track)
        
    # Within each album sort by disc number / track number
    album_track_sorted_list = []
    for key, value in album_sorted_dict.items():
        if key == "local_tracks":
            # DO SOMETHING HERE
            continue
        tmp = sorted(value, key=lambda element: (element['disc_number'], element['track_number']))
        album_track_sorted_list.append((tmp[0]['album_release_date'], [track['id'] for track in tmp]))

    # Order collection by release date
    album_track_sorted_list.sort()
    
    # Collapse it all into just a list of id's
    track_ids_ordered = []
    for album in album_track_sorted_list:
        track_ids_ordered += album[1]
        
    track_ids_ordered.remove(gsh.ORGANIZE_PLAYLIST_MACRO_ID)
    spotify.add_tracks_to_playlist(playlist_id, track_ids_ordered)
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Determines our playback state and if we should go through a macro.
INPUT: NA
OUTPUT: track_id of either current playing song or the song it just skipped to depending on if macro was triggered
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def handle_macro():
    track_id, shuffle_state, playlist_id = spotify.get_playback_state()
        
    if playlist_id != "":
        if track_id == gsh.SHUFFLE_MACRO_ID:
            track_id = shuffle_macro(shuffle_state, playlist_id)
            
        elif track_id == gsh.GEN_ARTIST_MACRO_ID:
            spotify.change_playback(skip="next")
            generate_artist_playlist_macro(playlist_id)
            track_id = ""
            
        elif track_id == gsh.DISTRIBUTE_TRACKS_MACRO_ID:
            spotify.change_playback(skip="next")
            distribute_tracks_to_playlists(playlist_id)
            track_id = ""
            
        elif track_id == gsh.ORGANIZE_PLAYLIST_MACRO_ID:
            spotify.change_playback(skip="next")
            reorganize_playlist(playlist_id)
            track_id = ""
    
    return track_id


def main():
    track_id = handle_macro()
    
    if track_id != "":
        log_track(track_id)


if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
