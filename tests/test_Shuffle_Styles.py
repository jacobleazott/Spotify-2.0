# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS FOR SHUFFLER                  CREATED: 2024-10-10          https://github.com/jacobleazott    ║  ║
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
    
    def test_weighted_shuffle(self):
        # We need to create a weighted db or mock it
        print("Not Implemented")
        
    def test_shuffle(self):
        print("Not Implemented")

        
if __name__ == "__main__":
    unittest.main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════