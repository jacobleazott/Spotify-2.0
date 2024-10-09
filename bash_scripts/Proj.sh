#!/bin/bash

source ~/projects/.venv/bin/activate
cd ~/projects/Spotify-2.0/
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
    "Update_Latest")
        python3 src/Latest_Hundred.py
        ;;
    "Playback_Tracker")
        # We occasionally get Address already in use errors likely because of cron runing jobs in parallel.
        #    Here we will just use a different redirect uri to deconflict them
        export SPOTIPY_REDIRECT_URI='http://localhost:9091'
        python3 src/Implementations.py
        sleep 15
        python3 src/Implementations.py
        sleep 15
        python3 src/Implementations.py
        sleep 15
        python3 src/Implementations.py
        ;;
    *)
        echo "Invalid Value"
esac
