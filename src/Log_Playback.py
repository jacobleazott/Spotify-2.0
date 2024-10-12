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
from datetime import datetime, timedelta

from decorators import *
from Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Populates our 'listening_db' and 'track_counts_db' with the passed in track_id. Note that this class does
                not require a GSH object as there is no spotify api call necessary.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogPlayback(LogAllMethods):
    track_id = ""
        
    def __init__(self, ldb_path: str=None, tcdb_path: str=None, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        self.ldb_path = ldb_path or Settings.LISTENING_DB
        self.tcdb_path = tcdb_path or Settings.TRACK_COUNTS_DB
        self.ldb_conn = None
        self.tcdb_conn = None
        
    def __exit__(self, exc_type, exc_value, traceback):
        if self.ldb_conn:
            self.ldb_conn.close()
        if self.tcdb_conn:
            self.tcdb_conn.close()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Either adds the new track to our track_count db or increments it by 1.
    INPUT: track_id - Id of track we are updating.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def increment_play_count_db(self) -> None:
        if not self.tcdb_conn:
            self.tcdb_conn = sqlite3.connect(self.tcdb_path)

        with self.tcdb_conn:
            self.tcdb_conn.execute(f'''CREATE TABLE IF NOT EXISTS 'tracks'(
                                     track_id TEXT PRIMARY KEY,
                                     play_count INTEGER NOT NULL);''')

            # Checks ot see if the track is already in the database or not
            if not bool(self.tcdb_conn.execute(
                    f"SELECT COUNT(*) from 'tracks' WHERE 'tracks'.track_id = '{self.track_id}'").fetchone()[0]):
                self.tcdb_conn.execute(f"""INSERT OR IGNORE INTO 'tracks'
                                            ('track_id', 'play_count') 
                                            VALUES (?, ?);""", (self.track_id, 1))
            else:
                self.tcdb_conn.execute(f"""UPDATE 'tracks'
                                            SET play_count = play_count + 1 
                                            WHERE track_id = '{self.track_id}'""")


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Reads our pickle file to determine if we have listened to the track for at least 30s and updates as
                 necessary.
    INPUT: track_id - What id we are currently listening to.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def update_last_track_count(self) -> None:
        try:
            with open(Settings.LAST_TRACK_PICKLE, 'rb') as fi:
                last_track_pickle = pickle.load(fi)
        except (EOFError, FileNotFoundError):
            last_track_pickle = "", False

        if last_track_pickle is None or last_track_pickle[0] != self.track_id:
            with open(Settings.LAST_TRACK_PICKLE, 'wb') as fi:
                pickle.dump((self.track_id, True), fi)
        elif last_track_pickle[1]:
            with open(Settings.LAST_TRACK_PICKLE, 'wb') as fi:
                pickle.dump((self.track_id, False), fi)
            self.increment_play_count_db()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Logs the current playing track into our listening.db.
    INPUT: track_id - Id of the track we are currently listening to.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def log_track(self, track_id):
        # Don't log if no track is present or it is one of our macros
        if track_id in Settings.MACRO_LIST or track_id == "":
            return

        self.track_id = track_id
        year = datetime.now().year
        
        if not self.ldb_conn:
            self.ldb_conn = sqlite3.connect(self.ldb_path)
        
        with self.ldb_conn:
            self.ldb_conn.execute(f'''CREATE TABLE IF NOT EXISTS '{year}'(
                                    track_id TEXT NOT NULL,
                                    time timestamp NOT NULL);''')

            timestamp = (datetime.now() - timedelta(
                seconds=int(datetime.now().strftime(r"%S")))).strftime(r"%Y-%m-%d %H:%M:%S")
            
            self.ldb_conn.execute(f"""INSERT INTO '{year}' ('track_id', 'time') 
                                     VALUES ("{track_id}", "{timestamp}");""")

        self.update_last_track_count()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════