#!/bin/bash

# PROJ_PATH should be defined in the cron.jobs file
cd $PROJ_PATH
source .venv/bin/activate
source tokens/spotify_token.sh
python3 src/Implementations.py