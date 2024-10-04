# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    INITIAL STARTUP                         CREATED: 2024-10-04          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file is to get a new user familiar with the code flow of this project. Most importantly however, it starts by
#   accessing the least amount of permissions and creates a backup of the entire user's library. This file should be
#   verified through some simple sqlite queries and be uploaded/ saved off somewhere safe. 
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from glob import glob

import General_Spotify_Helpers as gsh

from Backup_Spotify_Data import BackupSpotifyData
from Google_Drive_Uploader import DriveUploader
from Shuffle_Styles import Shuffler, ShuffleType
from decorators import *

logger = get_file_logger("logs/initial_startup.log", mode='a', console=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Initializes a spotify helper that only has access to read who you follow and your private playlists. It 
             then creates a full backup of your entire library into an sqlite db.
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def backup_entire_spotify_library() -> None:
    scopes = ["user-follow-read"
            , "playlist-read-private"]
    
    logger.info("Starting Up GSH and Authenticating...")
    spotify_obj = gsh.GeneralSpotifyHelpers(scopes=scopes)
    
    logger.info("Authentication Successful, Initializing Backup Object...")
    backup = BackupSpotifyData(spotify_obj, logger=logger)
    
    backup.backup_data()


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Initializes a spotify helper that only has access to reading the user's current playback. It then logs
             that for the user to see what they are currently playing.
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def grab_current_playback_and_display_info() -> None:
    scopes = ["user-read-playback-state"]

    logger.info("Starting Up GSH and Authenticating...")
    spotify_obj = gsh.GeneralSpotifyHelpers(scopes=scopes)
    
    logger.info("Authentication Successful, Grabbing User's Current Playback...")
    cur_track_id, shuffle_state, playlist_id = spotify_obj.get_playback_state()
    logger.info(f"Current Playback State, Track ID: {cur_track_id}, Shuffle State: " \
                f"{shuffle_state}, Playlist ID: {playlist_id}")
    
    track_name = spotify_obj.get_track_data(cur_track_id, info=['name'])
    logger.info(f"Track Name: {track_name}")
    
    playlist_name = spotify_obj.get_playlist_data(playlist_id, info=['name'])
    logger.info(f"Playlist Name: {playlist_name}")
    
    track_artists = spotify_obj.get_track_artists(cur_track_id, info=['id', 'name'])
    logger.info(f"Track Artists: {track_artists}")


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: This relies on already having a spotify library backup. Note how our scope doesn't need read access to the
             user's library since it will solely use the backup. It takes the user's current playing playlist and 
             randomly shuffles it and adds 80 tracks to the user's queue. If you have Spotify open you can see the
             queue being appended to in real time. This can take ~45 seconds to complete.
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def shuffle_current_playlist() -> None:
    scopes = ["user-read-playback-state"
            , "user-modify-playback-state"]

    logger.info("Starting Up GSH and Authenticating...")
    spotify_obj = gsh.GeneralSpotifyHelpers(scopes=scopes)
    
    logger.info("Authentication Successful, Grabbing User's Current Playback...")
    cur_track_id, shuffle_state, playlist_id = spotify_obj.get_playback_state()

    playlist_name = spotify_obj.get_playlist_data(playlist_id, info=['id', 'name'])
    logger.info(f"Currently Playling Playlist: {playlist_name}")
    
    shuffle_obj = Shuffler(spotify_obj, logger=logger)
    logger.info(f"Shuffling '{playlist_name[1]}'...")
    shuffle_obj.shuffle(playlist_id, ShuffleType.RANDOM)
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: This relies having the user already setting up their GMail API according to the README. This function
             just sends a simple test email with the current playing song name.
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def email_tester() -> None:
    SENDER_EMAIL = os.environ['GMAIL_USERNAME']
    RECIPIENT_EMAIL = os.environ['GMAIL_RECIPIENT']
    
    scopes = ["user-read-playback-state"]
    spotify_obj = gsh.GeneralSpotifyHelpers(scopes=scopes)
    cur_track_id, shuffle_state, playlist_id = spotify_obj.get_playback_state()
    track_name = spotify_obj.get_track_data(cur_track_id, info=['name'])[0]

    email_text = f"You're currently listening to '{track_name}'."
    msgRoot = MIMEText(email_text)
    msgRoot['Subject'] = "Test GMail API Messaging"
    msgRoot['From'] = SENDER_EMAIL
    msgRoot['To'] = RECIPIENT_EMAIL
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(SENDER_EMAIL, os.environ['GMAIL_TOKEN'])
        smtp_server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msgRoot.as_string())
        

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: This relies having the user already setting up their Google Drive API according to the README. This
             function uploads the latest file in your databases/backups directory.
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def google_drive_tester() -> None:
    latest_backup = max(glob(f"{BackupSpotifyData.DATABASE_LOCATION}*"), key=os.path.getmtime)
    DriveUploader(logger=logger).upload_file(latest_backup)


def main():
    backup_entire_spotify_library()
    # grab_current_playback_and_display_info()
    # shuffle_current_playlist()
    # email_tester()
    # google_drive_tester()

if __name__ == "__main__":
    main()


# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════