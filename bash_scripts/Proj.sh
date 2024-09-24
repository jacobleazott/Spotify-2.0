#!/bin/bash

cd ~/projects/Spotify_Release_Pi/
source .venv/bin/activate
source tokens/spotify_token.sh

case $1 in
    "Monthly_Release")
        python3 src/Monthly_Release.py
        ;;
    "Backup_Data")
        python3 src/Backup_Spotify_Data.py
        ;;
    "Weekly_Report")
        python3 src/Weekly_Report.py
        ;;
    "Playback_Tracker")
        # We occasionally get Address already in use errors likely because of cron runing jobs in parallel.
        #    Here we will just use a different redirect uri to deconflict them
        export SPOTIPY_REDIRECT_URI='http://localhost:9091'
        python3 src/Playback_Macro.py
        sleep 15
        python3 src/Playback_Macro.py
        sleep 15
        python3 src/Playback_Macro.py
        sleep 15
        python3 src/Playback_Macro.py
        ;;
    *)
        echo "Invalid Value"
esac
