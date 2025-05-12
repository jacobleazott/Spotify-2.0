# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SETTINGS AND CONSTANTS                   CREATED: 2024-10-07          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file solely holds our SettingsClass which is just a collection of "configurable" values that a user of the
#   project may want to change. It offers a single location for all files to reference. It utilizes a frozen dataclass
#   which means when we instantiate it as 'Settings' no inheriter can ever change these values. In this way we make a 
#   common location for immutable settings during runtime. I still leave the discretion to include constants in
#   individual files for 'magic' numbers that should NEVER change and shouldn't be 'easily' changed through these 
#   configurations.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import os
from dataclasses import dataclass

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that holds all of our user configurable settings/ constants for the project.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@dataclass(frozen=True)
class SettingsClass:
    
    MAX_NUM_PLAYLISTS: int  = 400
    MAX_QUEUE_LENGTH: int   = 80
    
    # Implementations
    MAX_RUNTIME_MINUTES: int    = 30
    LOGGING_RUNTIME_S: int      = 60
    LOGGING_INTERVAL_S: int     = 15
    
    # Macro IDs
    GEN_ARTIST_MACRO_ID: str          = "24NFf8j4Hc21IxQK7POU6f" # 'Creating New Melodies'
    DISTRIBUTE_TRACKS_MACRO_ID: str   = "2gps7VcJwo6nVmAxb9X3y2" # 'distributing'
    ORGANIZE_PLAYLIST_MACRO_ID: str   = "7mmImiqGDVDjH17htwQPeO" # 'Let's Organize'
    MACRO_LIST: tuple                 = (GEN_ARTIST_MACRO_ID, 
                                         DISTRIBUTE_TRACKS_MACRO_ID, 
                                         ORGANIZE_PLAYLIST_MACRO_ID)
    
    # Playlists
    PLAYLISTS_WE_CAN_DELETE_FROM: tuple = ("3dZVHLVdpOGlSy8oH9WvBi",) # 'The 100'
    MASTER_MIX_ID: str                  = "6kGQQoelXM2YDOSmqUUzRw"   # 'The Good - Master Mix'
    CHRISTMAS_MASTER_MIX_ID: str        = "3qki5BF8FMoFklkBdugQN6"   # 'The Good Christmas - Master Mix'
    PLAYLIST_IDS_NOT_IN_ARTISTS: tuple  = ("7Mgr45oWF0fzRzdlz0NNgT",) # 'Soundtracks - Master Mix'
    
    # Latest '100' Configuration
    LATEST_PLAYLIST_LENGTH: int = 255
    LATEST_SOURCE_PLAYLIST: str = MASTER_MIX_ID
    LATEST_DEST_PLAYLIST: str   = "3dZVHLVdpOGlSy8oH9WvBi" # Note this should be in PLAYLISTS_WE_CAN_DELETE_FROM, as a
                                                           #    safety percaution it is not a refernce but a duplicate.

    # Spotify API Scopes
    MAX_SCOPE_LIST: tuple = ("user-read-playback-state",
                             "user-modify-playback-state",
                             "playlist-read-private",
                             "user-follow-read",
                             "playlist-modify-public",
                             "playlist-modify-private")

    DELETE_SCOPE: str     = "DELETE-DELETE-DELETE"
    
    # Google Drive Configuration
    DRIVE_CLIENT_JSON: str      = "tokens/drive_client_secrets.json"
    DRIVE_TOKEN_FILE: str       = "tokens/google_drive_creds.txt"
    DRIVE_FOLDER_ID: str        = "16MR2FUanB13hnAGzbCx-ZZ3Pv04vqAAB"
    
    # Gmail Configuration
    SENDER_EMAIL: str           = os.getenv('GMAIL_USERNAME')
    RECIPIENT_EMAIL: str        = os.getenv('GMAIL_RECIPIENT')

    # DB Locations
    BACKUPS_LOCATION: str       = "databases/backups/"
    LISTENING_VAULT_DB: str     = "databases/listening_vault.db"
    LAST_TRACK_PICKLE: str      = "databases/lastTrack.pk"
    
    # Logging Settings
    FUNCTION_ARG_LOGGING_LEVEL: int = 15
    
    # Proxy Settings
    PROXY_SERVER_PORT: int = 5000


Settings = SettingsClass()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════