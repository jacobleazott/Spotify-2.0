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
from tkinter import *
import time
from io import BytesIO
import requests
from PIL import Image, ImageTk, ImageStat
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pathlib
import os, fnmatch
import glob
import shutil

scope = "user-read-currently-playing"
db_path = 'databases/'
track_info_db = "track_info.db"


def getResultInfo(results, first_elem='', item_elem='', info=['id']):
    elements = []
    next_link = ""
    while next_link is not None:
        # results = results[first_elem] if first_elem != '' else results
        for item in results['items']:
            item = item[first_elem][item_elem] if (item_elem != '' and first_elem != '') else\
                item[item_elem] if item_elem != '' else item
            tmp_list = [None for _ in range(len(info))]
            for idx, field in enumerate(info):
                tmp_list[idx] = item[field]
            if tmp_list[0] is not None:
                elements.append(tmp_list[0])
        next_link = results['next']
        results = sp.next(results)
    return elements


def getPlaylistTrackName(playlist_id):
    return getResultInfo(
        sp.playlist_items(playlist_id, fields="items, next")
        , item_elem='track', info=['name'])


def getPlaylistAlbumName(playlist_id):
    return getResultInfo(
        sp.playlist_items(playlist_id, fields="items, next")
        , first_elem='track', item_elem='album', info=['name'])


def getTrackData(track_id):
    track = sp.track(track_id)
    track_name = track["name"]
    artist_name = track["artists"][0]["name"]
    album_name = track["album"]["name"]
    album_id = track["album"]["id"]

    response = requests.get(track["album"]["images"][0]['url'])
    img = Image.open(BytesIO(response.content))
    img.save(f"Albums/{album_id}.png")

    conn = sqlite3.connect(track_info_db)

    conn.execute(f'''CREATE TABLE IF NOT EXISTS 'info'(
            track_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            album_name TEXT NOT NULL,
            album_id TEXT NOT NULL);''')

    conn.execute('INSERT INTO info (track_name,artist_name,album_name,album_id) VALUES (?,?,?,?)',
                 (track_name, artist_name, album_name, album_id))

    conn.commit()
    conn.close()

    return track_name, artist_name, album_name, album_id


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

playlist_id = "5SXOLxY7rlmwpIoR1HREdx"

tracks = getPlaylistTrackName(playlist_id)
albums = getPlaylistAlbumName(playlist_id)

file_searches = []


for idx, item in enumerate(tracks):
    # .replace(':', '')
    file_searches.append(f"{albums[idx].replace(':', '-')} * {item}")

print(len(tracks))
print(len(albums))
print(len(file_searches))


filepath = r"E:\Music\Spotify Local\Arbor Christmas\Arbor Christmas 320"
dest = r"E:\Music\Spotify Local\Christmas Local"
# filepath = r"E:\Music\Spotify Local\Arbor Christmas\Arbor Christmas 320\Arbor Christmas - Arbor Christmas- Volume 1"


def find(word, path):
    for file in glob.glob(os.path.join(path, f'**/*{word}*'), recursive=True):
        return file


for it in file_searches:
    print(it)
    src = find(it, filepath)
    print(src)
    shutil.copy(src, dest)
