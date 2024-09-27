# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    IMPLEMENTATIONS                          CREATED: 2024-09-24          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
from Spotify_Features import SpotifyFeatures
import General_Spotify_Helpers as gsh
from Shuffle_Styles import ShuffleType

def main():
    features = SpotifyFeatures(log_file_name="Playback.log")
    track_id, shuffle_enabled, playlist_id = features.get_playback_state()

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TRACK MACROS ════════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    match track_id:
        case gsh.SHUFFLE_MACRO_ID:
            shuffle_type = ShuffleType.WEIGHTED if shuffle_enabled else ShuffleType.RANDOM
            features.shuffle_playlist(playlist_id, shuffle_type)
            
        case gsh.GEN_ARTIST_MACRO_ID:
            features.skip_track()
            features.generate_artist_playlist_from_playlist(playlist_id)
            
        case gsh.DISTRIBUTE_TRACKS_MACRO_ID:
            features.skip_track()
            features.distribute_tracks_to_collections(playlist_id)
            
        case gsh.ORGANIZE_PLAYLIST_MACRO_ID:
            features.skip_track()
            features.organize_playlist_by_date(playlist_id)
            
        case _:
            features.log_playback_to_db(track_id)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # DATE TRIGGERS ═══════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        # Check Date/ Time
        #   Trigger Weekly Report
        #   Trigger Daily Backup
        #   Trigger Monthly Release
            

if __name__ == "__main__":
    main()

# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════