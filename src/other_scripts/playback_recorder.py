import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime, timedelta
from Levenshtein import distance
import logging as log
import threading
import pprint
import sqlite3
import sys
import time

db_path = r"databases\sessions.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()


def create_table():
    with conn:
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(
                        start TEXT NOT NULL UNIQUE,
                        end TEXT NOT NULL UNIQUE
                        );""")
        c.execute("""CREATE TABLE IF NOT EXISTS tracks(
                        session_id INTEGER,
                        spotify_id INTEGER,
                        FOREIGN KEY(session_id) REFERENCES sessions(id)
                        );""")


def start_session(start):
    with conn:
        c.execute(f"INSERT INTO sessions "
                  f"VALUES ('{start}', 'NA')")


def end_session(end):
    with conn:
        c.execute(f"SELECT * "
                  f"FROM sessions "
                  f"WHERE sessions.end='NA'")
        if len(c.fetchall()) > 0:
            c.execute(f"UPDATE sessions "
                      f"SET end = '{end}' "
                      f"WHERE sessions.end='NA'")


def gather_data(current_track, is_playing, start, end):
    while True:
        cur = sp.current_user_playing_track()
        if is_playing and current_track != cur['item']['id']:
            current_track = cur['item']['id']
            print("Adding New Track", current_track, cur['item']['name'])
        if not is_playing and cur['is_playing']:
            is_playing = True
            start = datetime.now().strftime("%Y-%m-%d_%H:%M")
            print("Starting Session", start)
            start_session(start)
        if is_playing and not cur['is_playing']:
            is_playing = False
            end = datetime.now().strftime("%Y-%m-%d_%H:%M")
            print("Ending Session From", start, "To", end)
            end_session(end)
        time.sleep(1)


last_month = datetime.today().replace(day=1) - timedelta(days=1)
log.basicConfig(filename=f'logs/Release-{last_month.year}-{last_month.month:02d}.log', level=log.INFO, filemode='w',
                format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S')

scope = "user-read-currently-playing"
db_path = 'databases/'

redirect_uri = r"http://localhost:5555/callback/"
f = open(r"tokens/client_info.txt", 'r')
client_id = f.readline().rstrip()
client_secret = f.readline().rstrip()
users = [f.readline().rstrip(), f.readline().rstrip()]


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                               username=users[0],
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               open_browser=False))

playlist_id = "6swK7zASOuXcoNxCNiTxnQ"


create_table()
gather_data(0, False, None, None)

print("----------------------")
