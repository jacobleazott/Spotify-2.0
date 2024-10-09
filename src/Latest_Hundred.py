# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    LATEST 100                               CREATED: 2024-09-26          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Description not needed since this will be deleted soon and added to Misc_Features.py
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging

import General_Spotify_Helpers as gsh
from decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Updates 'DEST_PLAYLIST' to include the latest 'PLAYLIST_LENGTH' tracks from our 'SOURCE_PLAYLIST'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LatestTracksPlaylist():
    PLAYLIST_LENGTH = 100
    SOURCE_PLAYLIST = "6kGQQoelXM2YDOSmqUUzRw"
    DEST_PLAYLIST = "3dZVHLVdpOGlSy8oH9WvBi"
    FEATURE_SCOPES = ["playlist-read-private"
                    , "playlist-read-collaborative"
                    , "playlist-modify-public"
                    , "playlist-modify-private"
                    , "DELETE-DELETE-DELETE"]

    def __init__(self, spotify, logger: logging.Logger=None) -> None:
        self.spotify = spotify
        self.spotify.scopes = self.FEATURE_SCOPES
        self.logger = logger if logger is not None else logging.getLogger()
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Grabs the latest 100 tracks from 'The Good' and adds them to our 'The 100' Playlist after clearing it.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def update_100_playlist(self):
        # Grab # of tracks of The Good, subtract 100 to get offset
        offset = self.spotify.get_playlist_data(self.SOURCE_PLAYLIST, info=[['tracks', 'total']])[0] - 100
        tracks = [track['id'] for track in self.spotify.get_playlist_tracks(self.SOURCE_PLAYLIST, offset=offset)]

        self.spotify.remove_all_playlist_tracks(self.DEST_PLAYLIST, max_playlist_length=100)
        self.spotify.add_tracks_to_playlist(self.DEST_PLAYLIST, tracks)

def main():
    spotify = gsh.GeneralSpotifyHelpers()
    test = LatestTracksPlaylist(spotify)
    test.update_100_playlist()


if __name__ == "__main__":
    main()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════