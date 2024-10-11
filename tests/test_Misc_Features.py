# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS FOR MISC FEATURES             CREATED: 2024-10-10          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import sys
import unittest
from pprint import pprint

# Override 'spotipy' with our local 'mocked_spotipy.py' MUST BE DONE BEFORE GSH
sys.modules['spotipy'] = __import__('mocked_spotipy')

import General_Spotify_Helpers as gsh
import tester_helpers as thelp
from Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all GSH functionality
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestGSH(unittest.TestCase):
    
    def test_get_first_artist_from_playlist(self):
        # assert False
        print("Not Implemented")
        
    def test_generate_artist_release(self):
        print("Not Implemented")
        
    def test_distribute_tracks_to_collections_from_playlist(self):
        print("Not Implemented")
        
    def test_reorganize_playlist(self):
        print("Not Implemented")
        
    def test_update_daily_latest_playlist(self):
        print("Not Implemented")
    
        
if __name__ == "__main__":
    unittest.main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════