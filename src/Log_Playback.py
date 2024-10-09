# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    LOG CURRENT PLAYBACK                     CREATED: 2021-07-20          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import pickle
import sqlite3
import logging
from datetime import datetime, timedelta

from decorators import *
import General_Spotify_Helpers as gsh

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogPlayback(LogAllMethods):
    PICKLE_FILENAME = "databases/lastTrack.pk"
    LISTENING_DB = "databases/listening_data.db"
    TRACK_COUNTS_DB = "databases/track_counts.db"
    track_id = ""
        
    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Either adds the new track to our track_count db or increments it by 1.
    INPUT: track_id - Id of track we are updating.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def increment_play_count_db(self) -> None:
        track_counts_conn = sqlite3.connect(self.TRACK_COUNTS_DB)
        track_counts_conn.execute(f'''CREATE TABLE IF NOT EXISTS 'tracks'(
             track_id TEXT PRIMARY KEY,
             play_count INTEGER NOT NULL);''')

        # Checks ot see if the track is already in the database or not
        if not bool(track_counts_conn.execute(
                f"SELECT COUNT(*) from 'tracks' WHERE 'tracks'.track_id = '{self.track_id}'").fetchone()[0]):
            track_counts_conn.execute(f"""INSERT INTO 'tracks'
                              ('track_id', 'play_count') 
                              VALUES (?, ?);""", (self.track_id, 1))
        else:
            track_counts_conn.execute(f"""UPDATE 'tracks'
                                SET play_count = play_count + 1 
                                WHERE track_id = '{self.track_id}'""")

        track_counts_conn.commit()
        track_counts_conn.close()


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Reads our pickle file to determine if we have listened to the track for at least 30s and updates as
                 necessary.
    INPUT: track_id - What id we are currently listening to.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def update_last_track_count(self) -> None:
        try:
            with open(self.PICKLE_FILENAME, 'rb') as fi:
                last_track_pickle = pickle.load(fi)
        except (EOFError, FileNotFoundError):
            last_track_pickle = "", False

        if last_track_pickle is None or last_track_pickle[0] != self.track_id:
            with open(self.PICKLE_FILENAME, 'wb') as fi:
                pickle.dump((self.track_id, True), fi)
        elif last_track_pickle[1]:
                with open(self.PICKLE_FILENAME, 'wb') as fi:
                    pickle.dump((self.track_id, False), fi)
                self.increment_play_count_db()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Logs the current playing track into our listening.db.
    INPUT: track_id - Id of the track we are currently listening to.
    OUTPUT: NA
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def log_track(self, track_id):
        # Don't log if no track is present or it is one of our macros
        if track_id in gsh.MACRO_LIST + [""]:
            return

        self.track_id = track_id
        year = datetime.now().year
        ldb_conn = sqlite3.connect(self.LISTENING_DB)

        ldb_conn.execute(f'''CREATE TABLE IF NOT EXISTS '{year}'(
                track_id TEXT NOT NULL,
                time timestamp NOT NULL);''')

        timestamp = (datetime.now() - timedelta(
            seconds=int(datetime.now().strftime(r"%S")))).strftime(r"%Y-%m-%d %H:%M:%S")
        
        ldb_conn.execute(f"""INSERT INTO '{year}' ('track_id', 'time') 
                         VALUES ("{track_id}", "{timestamp}");""")
        ldb_conn.commit()
        ldb_conn.close()

        self.update_last_track_count()
    
# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════