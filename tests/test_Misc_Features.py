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
sys.modules['spotipy'] = __import__('helpers.mocked_spotipy')

import src.General_Spotify_Helpers as gsh
import tests.helpers.tester_helpers as thelp
from src.helpers.Settings import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all GSH functionality
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestMiscFeatures(unittest.TestCase):
    
    def test_get_first_artist_from_playlist(self):
        # I think we need to think really hard about mocking Settings.py
        #   We could go back and have manual control over all of the other Settings
        #   We have been using. This file is going to need it a lot more than others
        #   Mostly when it comes to the macro list, master playlist, and the 'latest'.
        
        # This is also where we are really going to be tested on whether or not I wrote
        #   good code. I think for the date part of generate artist we can skip some of it
        #   since we unit test that function heavily. But we could really treat this
        #   almost as a small integration test.
        
        # We could think about putting out all of these features as PR... But I still
        #   do want to test Spotify_Features.py and Implementations.py. Those unit tests
        #   will be... interesting, the way we have structured the code it seems more 
        #   fruitless to be specifically testing that spotipy did its job correctly.
        #   and even when we get up to the Implementations I don't think we care about
        #   it 'doing' anything. I think that will just be 100% mocked features object
        #   that we are solely concerned with making sure it triggers as necessary. The
        #   threading and the apscheduler will be reaaaly fun to deal with.
        
        # Spotify features will be in a similar boat. For some of them I will care that
        #   they output something specific, but for most it is literally just me passing
        #   ref to their respective function. So maybe just a simple 'assert is called'
        #   would suffice. 
        
        # This is turning out so good though, once we have all this tech debt flushed out
        #   we have a project to be really proud of. Something that has more testing
        #   code then src code. Something we can have ever so increased faith in that it
        #   does what we want, and it does it well. Well as well as we code it in python.
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