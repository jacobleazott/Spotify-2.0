#!/bin/bash

# PROJ_PATH should be defined in the cron.jobs file
if [ -n "$PROJ_PATH" ]; then
    cd "$PROJ_PATH"
fi
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
source .venv/bin/activate
source tokens/spotify_token.sh
python3 src/proxy/Spotify_Proxy_Server.py