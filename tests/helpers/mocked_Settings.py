# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    MOCKED SETTINGS                          CREATED: 2024-10-12          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
from dataclasses import dataclass

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# @dataclass(frozen=False)  # Remove frozen to allow modifications in tests
class MockedSettingsClass():
    
    MAX_NUM_PLAYLISTS: int  = 10
    MAX_QUEUE_LENGTH: int   = 5
    
    # Implementations
    MAX_RUNTIME_MINUTES: int    = 30
    LOGGING_RUNTIME_S: int      = 60
    LOGGING_INTERVAL_S: int     = 15
    
    # Macro IDs
    SHUFFLE_MACRO_ID: str             = "Tr999"
    GEN_ARTIST_MACRO_ID: str          = "Tr998"
    DISTRIBUTE_TRACKS_MACRO_ID: str   = "Tr997"
    ORGANIZE_PLAYLIST_MACRO_ID: str   = "Tr996"
    MACRO_LIST: tuple                 = [SHUFFLE_MACRO_ID, 
                                         GEN_ARTIST_MACRO_ID, 
                                         DISTRIBUTE_TRACKS_MACRO_ID, 
                                         ORGANIZE_PLAYLIST_MACRO_ID]
    
    # Playlists
    PLAYLISTS_WE_CAN_DELETE_FROM: tuple = ["Pl111"] # 'The 100'
    MASTER_MIX_ID: str                  = "Pl222"   # 'The Good - Master Mix'
    PLAYLIST_IDS_NOT_IN_ARTISTS: tuple  = ["Pl333"] # 'Soundtracks - Master Mix'
    
    # Latest '100' Configuration
    LATEST_PLAYLIST_LENGTH: int = 10
    # LATEST_SOURCE_PLAYLIST: str = MASTER_MIX_ID
    LATEST_DEST_PLAYLIST: str   = "Pl444" # Note this should be in PLAYLISTS_WE_CAN_DELETE_FROM, as a
                                                           #    safety percaution it is not a refernce but a duplicate.

    # Spotify API Scopes
    MAX_SCOPE_LIST: tuple = ["user-read-playback-state",
                             "user-modify-playback-state",
                             "playlist-read-private",
                             "user-follow-read",
                             "playlist-modify-public",
                             "playlist-modify-private"]

    DELETE_SCOPE: str     = "DELETE-DELETE-DELETE"
    
    # Google Drive Configuration
    DRIVE_CLIENT_JSON: str      = "fake_path/fake_creds.json"
    DRIVE_TOKEN_FILE: str       = "fake_path/fake_creds.txt"
    DRIVE_FOLDER_ID: str        = "fake_folder-1"
    
    # Gmail Configuration
    SENDER_EMAIL: str           = "fake.sender@unknown.com"
    RECIPIENT_EMAIL: str        = "fake.receiver@unknown.com"

    # DB Locations
    BACKUPS_LOCATION: str       = "fake_path/fake_backups/"
    LAST_TRACK_PICKLE: str      = "fake_path/fake_pickle.pk"
    LISTENING_DB: str           = "fake_path/fake_ldb.db"
    TRACK_COUNTS_DB: str        = "fake_path/fake_tcdb.db"
    
    # Logging Settings
    FUNCTION_ARG_LOGGING_LEVEL: int = 15
    

Test_Settings = MockedSettingsClass()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
