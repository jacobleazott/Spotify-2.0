# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    IMPLEMENTATIONS                         CREATED: 2024-09-24          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This class is our entry point into all of our automated features we want to use. This should be the file that is run
#   from cron (through a shell script with venv and tokens setup) every minute. This is 'configurable' but hasn't been
#   tested. 
#
# METHODOLOGY -
# For track/ playback triggered events we currently run our 'log_and_macro' function through apscheduler to
#   periodically log our playback, and trigger macros. To make sure we are always logging, when a 'macro' is triggered
#   we create an entirely new SpotifyFeatures object and send it off on its own thread. This allows us to log and run
#   macros in parallel which can be very helpful if our macros take an extended amount of time.
#
# For time based events such as monthly releases, nightly backups, or weekly reports we use the 'check_date_time' 
#   function based upon the start time of our script. This does rely on cron and our shell script to start us within
#   a 'reasonable' amount of time in the minute trigger. It also currently has no way of realizing if it 'missed' a 
#   trigger in the case of a cron edge case or even if the server was just down. This is an improvement I have planned
#   in BRO-87. Regardless unlike the 'macros' above that are run in parallel these features are run sequentially. This
#   is done for a few reasons, the biggest being api response rate, database changes, and simplicity. These timed
#   triggers usually happen very early in the morning when we aren't even using spotify so if it takes 10 mins to
#   complete vs. 4 mins parallel it doesn't really affect us.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import os
import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval     import IntervalTrigger
from datetime                          import datetime, timedelta

from src.features.Shuffle_Styles import ShuffleType
from src.Spotify_Features        import SpotifyFeatures
from src.helpers.Settings        import Settings

threads = []

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Monitor method that when run as a seperate thread will exit the program if it goes over our set time.
             This is very helpful if we are ever worried about our service hanging. This can automatically do cleanup.
INPUT: N/A
OUTPUT: N/A
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def monitor_script_runtime():
    start_time = datetime.now()
    while True:
        if datetime.now() - start_time > timedelta(minutes=Settings.MAX_RUNTIME_MINUTES):
            print("Script has been running for too long. Exiting...")
            os._exit(1)
        time.sleep(60)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Spins up a new thread with a new SpotifyFeature object so our main loop can continue.
INPUT: method - Func that we will be calling from SpotifyFeatures.
       args - List of args we are passing to 'method'.
       log_file_name - Log filename we want to use.
       kwargs - List of kwargs we are passing to 'method'.
OUTPUT: N/A, it does however add the thread to the global 'threads'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def startup_feature_thread(method, *args, log_file_name="Default.log", run_parallel=True, **kwargs):
    global threads
    tmp_feature = SpotifyFeatures(log_file_name=log_file_name)
    # Here we bind the method we passed in to our new class. Prevents us from unnecessarily creating new objects
    bound_method = method.__get__(tmp_feature)
    thread = threading.Thread(target=bound_method, args=args, kwargs=kwargs, daemon=True)
    thread.start()

    if run_parallel:
        threads.append(thread)
    else:
        thread.join()
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Used to determine if the 'cur_time' meets the trigger defined by our timing args. 
             If neither 'day' or 'weekday' is passed in we assume it to be triggered daily on 'hour' and 'minutes'.
             If 'weekday' is passed in, it is a weekly trigger where it will happen on that 'weekday' and time.
             If 'day' is passed in, it is a monthly trigger where it will happen on that 'day' and time of the month.
INPUT: cur_time - Current time we want to compare against, this is passed in since we usually run sequentially and 
                    don't want to trigger multiple times OR miss our trigger.
       day - Day of the month we want to trigger on (1-31).
       weekday - Day of the week we want to trigger on (0-6).
       hour - Hour we want to trigger on (0-23).
       minute - Minute we want to trigger on (0-59).
OUTPUT: Bool on whether the cur_time meets the trigger event defined by the time args passed in.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def check_date_time(cur_time: datetime, day: int=None, weekday: int=None, hour: int=None, minute: int=None) -> bool:
    if hour is None or minute is None:
        return False
    daily_trigger = day is None and weekday is None
    weekly_trigger = weekday is not None and cur_time.weekday() == weekday
    monthly_trigger = day is not None and cur_time.day == day
    return cur_time.hour == hour and cur_time.minute == minute and \
        (daily_trigger or weekly_trigger or monthly_trigger)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Grabs current playback, triggers any macros based upon the playback by starting up a new SpotifyFeatures
             thread. Additionally, assuming no macro was triggered logs the track_id to our listening databases.
INPUT: spotify_features - SpotifyFeatures object we will use to grab playback, and call the log playback to.
OUTPUT: N/A
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def log_and_macro(spotify_features) -> None:
    playback = spotify_features.get_playback_state()
    
    if playback is None:
        return
    
    # Only Trigger Macros If We Are Playing A Playlist
    if playback['context'] is not None and playback['context']['type'] == "playlist":
        if playback['repeat_state'] != "off":
            spotify_features.set_repeat_state('off')
            shuffle_type = ShuffleType.WEIGHTED if playback['shuffle_state'] else ShuffleType.RANDOM
            startup_feature_thread(SpotifyFeatures.shuffle_playlist
                                   , playback['context']['id']
                                   , shuffle_type=shuffle_type
                                   , log_file_name="Shuffle-Playlist.log")
        else:
            match playback['track']['id']:
                case Settings.GEN_ARTIST_MACRO_ID:
                    spotify_features.skip_track()
                    startup_feature_thread(SpotifyFeatures.generate_artist_playlist_from_playlist
                                           , playback['context']['id']
                                           , log_file_name="Generate-Artist-Playlist.log")

                case Settings.DISTRIBUTE_TRACKS_MACRO_ID:
                    spotify_features.skip_track()
                    startup_feature_thread(SpotifyFeatures.distribute_tracks_to_collections
                                           , playback['context']['id']
                                           , log_file_name="Distribute-Tracks.log")

                case Settings.ORGANIZE_PLAYLIST_MACRO_ID:
                    spotify_features.skip_track()
                    startup_feature_thread(SpotifyFeatures.organize_playlist_by_date
                                           , playback['context']['id']
                                           , log_file_name="Organize-Playlist.log")

    spotify_features.log_playback_to_db(playback)
            

def main():
    global threads
    start_time = datetime.now()
    
    # Startup our monitor thread to make sure if anything hangs in our program we will exit 'eventually'
    monitor_thread = threading.Thread(target=monitor_script_runtime, daemon=True)
    monitor_thread.start()
    
    features = SpotifyFeatures(log_file_name="Playback.log")
    
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # PERIODIC TRIGGERS ══════════════════════════════════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Setup log_and_macro to be run over the next 'LOGGING_RUNTIME_S' every 'LOGGING_RUNTIME_S'
    scheduler = BackgroundScheduler()
    scheduler.add_job(log_and_macro, IntervalTrigger(seconds=Settings.LOGGING_INTERVAL_S), args=[features], 
                      next_run_time=datetime.now())
    scheduler.start()
    time.sleep(Settings.LOGGING_RUNTIME_S - Settings.LOGGING_INTERVAL_S)
    # Even though we shutdown if a log_and_macro is still running it will continue to run until exit.
    scheduler.shutdown()

    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # DATE TRIGGERS ══════════════════════════════════════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Backup Library - Run Every Day At 2 AM
    if check_date_time(start_time, hour=2, minute=0):
        startup_feature_thread(SpotifyFeatures.backup_spotify_library
                               , log_file_name="Backup-Library.log"
                               , run_parallel=False)
    
    # Update 'Latest' Playlist - Run Every Day At 2 AM
    if check_date_time(start_time, hour=2, minute=0):
        startup_feature_thread(SpotifyFeatures.update_daily_latest_playlist
                               , log_file_name="Update-Latest-Playlist.log"
                               , run_parallel=False)
    
    # Weekly Report - Run Every Monday At 3 AM
    if check_date_time(start_time, weekday=0, hour=3, minute=0):
        startup_feature_thread(SpotifyFeatures.generate_weekly_report
                               , log_file_name="Weekly-Report.log"
                               , run_parallel=False)
    
    # Upload Library Backup To Google - Run Every Sunday and Wednesday At 2 AM
    if check_date_time(start_time, weekday=6, hour=2, minute=0) \
            or check_date_time(start_time, weekday=2, hour=2, minute=0):
        startup_feature_thread(SpotifyFeatures.upload_latest_backup_to_drive
                               , log_file_name="Drive-Upload.log"
                               , run_parallel=False)

    # Monthly Release - Run The 1st of Every Month At 1 AM
    if check_date_time(start_time, day=1, hour=1, minute=0):
        startup_feature_thread(SpotifyFeatures.generate_monthly_release
                               , log_file_name="Monthly-Release.log"
                               , run_parallel=False)
    # ════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    # We want to wait for any threads we triggered in our playback macros to not cut them off early.
    [thread.join() for thread in threads]
    
    # Small sleep just to make sure all threads have exited gracefully
    time.sleep(1)


if __name__ == "__main__":
    main()


# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════