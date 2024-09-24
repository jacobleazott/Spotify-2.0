# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    GENERATE FULL DISCOGRAPHY PLAYLIST      CREATED: 2024-01-05          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Generates a playlist with every single track an artist has put out, or has appeared on.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

import General_Spotify_Helpers as gsh
import re

SCOPE = ["playlist-modify-public"
       , "playlist-modify-private"
       , "playlist-read-private"]

spotify = gsh.GeneralSpotifyHelpers(SCOPE)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Queries user for a valid artist id
INPUT: NA
OUTPUT: artist_id (str) and artist_name (str)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def prompt_user_for_artist_id():
    artist_link = input("Please Enter The Artist Link To Generate A Playlist For: ")
    artist_id = re.split('[/?]', artist_link)[4]
    artist_name = spotify.get_artist_data(artist_id, ['name'])[0]
    return artist_id, artist_name if input(f"Is The Following Artist Correct?" \
                                           + f": {artist_name} : [y/n]: ") == 'y' else exit(1)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates a full discography playlist of artist entered by user
INPUT: NA
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_artist_playlist():
    artist_id, artist_name = prompt_user_for_artist_id()
    tracks = spotify.gather_tracks_by_artist(artist_id)
    playlist_id = spotify.create_playlist(f"{artist_name} GO THROUGH", description=f"All the tracks from {artist_name}")
    spotify.add_tracks_to_playlist(playlist_id, tracks)


def main():
    generate_artist_playlist()
    

if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════