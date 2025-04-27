# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SMART INTERFACE DB v API                 CREATED: 2025-04-25          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


from src.helpers.Database_Helpers   import DatabaseHelpers, DatabaseSchema, SCHEMA_FIELDS
from src.helpers.decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SmartInterface(LogAllMethods):
    
    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.logger = logger if logger is not None else logging.getLogger()
        self.db = DatabaseHelpers(logger=self.logger)
    
    
    # List of methods
    #     def get_user_artists(self, info: list[str]=['id']) -> list[dict]:
    #     def get_user_playlists(self)
    #     def get_playlist_tracks(self, playlist_id: str, offset: int=0,
    #     def get_several_tracks(self, track_ids: list[str], info: list[str]=['id']) -> list[dict]:
    #     def get_track_artists(self, track_id: str, info: list[str]=['id']) -> list[str]:
    #     def get_track_data(self, track_id: str, info: list[str]=['id']) -> list[str]:
    #     def get_artist_data(self, artist_id: str, info: list[str]=['id']) -> list[str]:
    #     def get_album_data(self, album_id: str, info: list[str]=['id']) -> list[str]:
    #     def get_playlist_data(self, playlist_id: str, info: list[str]=['id']) -> list[str]:
    
    
    # List of "maybe" methods, these likely will always be incomplete and we won't know
    #     get_artist_albums(self, artist_id:str, 
    #     gather_tracks_by_artist(self, artist_id:str, 
    #     get_albums_tracks(self, album_ids: list[str], 


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════