# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    PLAYBACK MACRO UNIT TESTS               CREATED: 2024-07-06          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This file is to create some basic unit tests for the Playback_Macro.py script
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import random
import datetime

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def make_weighted_snippet(track_data, QUEUE_LENGTH):
    track_data.sort()
    
    tmp_play_count = 0
    tmp_track_count_group = []
    track_count_groupings = []

    for idx, track in enumerate(track_data):
        if track[0] > tmp_play_count and len(tmp_track_count_group) > 0:
            track_count_groupings.append(tmp_track_count_group)
            tmp_play_count = track[0]
            tmp_track_count_group = []
            if idx >= QUEUE_LENGTH:
                break
        tmp_track_count_group.append(track[1])
        # print(tmp_track_count_group)
    track_count_groupings.append(tmp_track_count_group)
        
    # Now we randomize each "set" of track_counts individually and add them up to one master list
    track_list = []
    # random.seed(datetime.datetime.now().timestamp())
   
    for track_group in track_count_groupings:
        # random.shuffle(track_group)
        track_list += track_group
    
    return track_list[:min(len(track_list), QUEUE_LENGTH)]



def main():
    random.seed(datetime.datetime.now().timestamp())
    
    test_set_1 = [(0, 'a'), (1, 'b'), (1, 'c'), (2, 'd'), (2, 'e')]
    res_1a = ['a', 'b', 'c', 'd', 'e']
    res_1b = ['a', 'b', 'c']
    
    if (make_weighted_snippet(test_set_1, 5) != res_1a):
        print("FAILURE TEST 1a")
            
    if (make_weighted_snippet(test_set_1, 3) != res_1b):
        print("FAILURE TEST 1b")
        
    if (make_weighted_snippet(test_set_1, 10) != res_1a):
        print("FAILURE TEST 1c")
        
    random.shuffle(test_set_1)
    if (make_weighted_snippet(test_set_1, 5) != res_1a):
        print("FAILURE TEST 1c")
        
    test_set_2 = [(1, 'a'), (1, 'b'), (65, 'c'), (400, 'd'), (1000, 'e')]
    res_2a = ['a', 'b', 'c', 'd', 'e']
    res_2b = ['a', 'b', 'c']
        
    if (make_weighted_snippet(test_set_2, 10000) != res_2a):
        print("FAILURE TEST 2a")
            
    if (make_weighted_snippet(test_set_2, 3) != res_2b):
        print("FAILURE TEST 2b")



if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════



