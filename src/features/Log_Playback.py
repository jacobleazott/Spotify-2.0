# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    LOG CURRENT PLAYBACK                     CREATED: 2021-07-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# The use of this file is to simply log a given track_id not only to our 'listening_db' with a timestamp. But also to
#   update 'track_counts.db' with "listened" songs. The 'listening_db' is great for calculating listening time, and 
#   always having a clear log of all of our listening if we ever want to do something with it. The 'track_counts.db' 
#   technically could always be recreated but it's just easier to build it as we go. The idea of this db is to hold how
#   many times we have listened to a given track. For my implementation "listening" counts as having the same song
#   being passed in back to back calls to this function. (To save this data between script runs we store it in a pickle
#   file). This might one day be improved to include a timestamp in the pickle file so it's not dependent on frequency
#   of calls. However, right now we query ever 15s so we count a track as listened if we've listened to 16-30s of it.
#   This gives us an ability to immediately skip songs and not worry about it counting against us in later features.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import pickle
import sqlite3
from datetime import datetime

from src.helpers.Database_Helpers   import DatabaseHelpers, build_entries_from_tracks
from src.helpers.decorators import *
from src.helpers.Settings   import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Populates our listening_connection and track_count. Note that this class does not require a GSH object 
                as there is no spotify api call necessary.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogPlayback(LogAllMethods):        
    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        self.vault_db = DatabaseHelpers(logger=self.logger)
        self.track = {}

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Either adds the new track to our track_count db or increments it by 1.
    INPUT: N/A
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def increment_play_count_db(self) -> None:
        with self.vault_db.connect_db() as db_conn:
            # This will insert a new row if it doesn't exist, or update if it does
            db_conn.execute("""
                INSERT INTO track_play_counts (id_track, play_count)
                VALUES (?, 1)
                ON CONFLICT(id_track) DO UPDATE SET play_count = play_count + 1;
            """, (self.track['id'],))

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Reads our pickle file to determine if we have listened to the track for at least 30s and updates as
                 necessary.
    INPUT: N/A
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def update_last_track_count(self) -> None:
        try:
            with open(Settings.LAST_TRACK_PICKLE, 'rb') as fi:
                last_track_pickle = pickle.load(fi)
        except (EOFError, FileNotFoundError):
            last_track_pickle = "", False

        if last_track_pickle is None or last_track_pickle[0] != self.track['id']:
            with open(Settings.LAST_TRACK_PICKLE, 'wb') as fi:
                pickle.dump((self.track['id'], True), fi)
        elif last_track_pickle[1]:
            with open(Settings.LAST_TRACK_PICKLE, 'wb') as fi:
                pickle.dump((self.track['id'], False), fi)
            self.increment_play_count_db()
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Logs the current playing track into our listening.db.
    INPUT: playback - Dictionary of current playback, see 'get_playback_state()' in GSH.
           inc_track_count - Whether we should increment our track_count database.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def log_track(self, playback: dict, inc_track_count: bool) -> None:
        if playback is None \
            or playback['is_playing'] == False \
            or playback['track']['id'] in Settings.MACRO_LIST:
            return
        
        self.track = playback['track']
        self.track['id'] = self.track['id'] if self.track is not None else f"local_track_{self.track['name']}"
        
        entries = build_entries_from_tracks([self.track])
        for table, values in entries.items():
            print(table, values)
            self.vault_db.insert_many(table, values)

        with self.vault_db.connect_db() as db_conn:
            db_conn.execute(f"""INSERT INTO 'listening_session' ('time', 'id_track') VALUES (?, ?);""", 
                                  (datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"), self.track['id']))
        if inc_track_count:
            self.update_last_track_count()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════