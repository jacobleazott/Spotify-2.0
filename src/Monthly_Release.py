# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    MONTHLY RELEASE RADAR                   CREATED: 2020-06-05          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Because spotify is dumb I need to create my own release tracker. This script takes all of the artists followed by
#   the user and creates a 'release radar' for the last month. This includes every single track that each of those
#   artists put out/ appeared on that past month. 
#
# If desired you can specify START_DATE and END_DATE for a custom range, if left blank it defaults to the last month
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
from datetime import datetime, timedelta
import logging as log
import re

import General_Spotify_Helpers as gsh
from decorators import *


SCOPE = ["user-follow-read"
       , "playlist-read-private"
       , "playlist-modify-public"
       , "playlist-modify-private"]

START_DATE = "" # datetime.date(2024, 3, 30)
END_DATE = "" # datetime.date(2024, 5, 30)

last_month = datetime.today().replace(day=1) - timedelta(days=1)
log.basicConfig(filename=f'logs/Release-{last_month.year}-{last_month.month:02d}.log', level=log.INFO, filemode='w',
                format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S')

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Gathers all tracks from the user's followed artists that have been released within the date range
INPUT: spotify - GeneralSpotifyHelpers instance for that user
       start_date - (datetime) start of our date range we will return for
       end_date - (datetime) end of our date range we will return for
OUTPUT: list of track ids found in the time range from all of the user's artists
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@logfunc
def gather_release_tracks(spotify, start_date, end_date):
    log.info(f"Gathering Releases For: {start_date.strftime('%b %d %Y')}-{end_date.strftime('%b %d %Y')}")
    tracks = list()

    for artist in sorted(spotify.get_user_artists(info=['id', 'name']), key=lambda x: x['name']):
        log.info(f"Finding New Releases For \"{artist['name']}\" ID: {artist['id']}")
        artist_tracks = spotify.gather_tracks_by_artist(artist['id'], start_date, end_date)
        log.info(f"\t\t Found {len(artist_tracks)} New Tracks")
        tracks += artist_tracks

    return tracks


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates a 'release' playlist for the time range (previous month if blank) of all the given user's artists
INPUT: spotify - GeneralSpotifyHelpers instance for that user
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@logfunc
def monthly_release(spotify):
    global START_DATE, END_DATE
    playlist_name = ""

    if (START_DATE == "" or END_DATE == ""):
        last_month = datetime.today().replace(day=1) - timedelta(days=1)
        START_DATE = datetime(last_month.year, last_month.month, 1)
        END_DATE = START_DATE.replace(day=last_month.day)
        playlist_name = f"Release Radar: {START_DATE.month:02d}-{START_DATE.year}"
    else:
        playlist_name = f"Release Radar: {start_date.strftime('%b %d %Y')}-{end_date.strftime('%b %d %Y')}"

    tracks = gather_release_tracks(spotify, START_DATE, END_DATE)
    log.info(f"=======================================================================")
    log.info(f"Total Tracks: {len(tracks)}")
    log.info(f"{tracks}")
    log.info(f"Creating Playlist")
    playlist_id = spotify.create_playlist(playlist_name)
    log.info(f"Created Playlist, Name: {playlist_name}, {playlist_id}")
    log.info(f"Adding Tracks")
    spotify.add_tracks_to_playlist(playlist_id, tracks)

@logfunc
def main():
    f = open(r"tokens/usernames.txt", 'r')
    users = [f.readline().rstrip(), f.readline().rstrip()]
    # users = [f.readline().rstrip()]

    for username in users:
        spotify = gsh.GeneralSpotifyHelpers(SCOPE, username=username)

        if len(spotify.get_user_playlists()) < 400:
            monthly_release(spotify)
        else:
            log.warning("User Has More Than 400 Playlists")

        log.info(f"Finished Release For User {spotify.username}")


if __name__ == "__main__":
    main()
    
# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════