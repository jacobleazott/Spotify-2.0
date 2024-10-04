#!/bin/bash

export PYTHONPATH=$(pwd)/src:$PYTHONPATH
source .venv/bin/activate
source tokens/spotify_token.sh
python3 startup/Initial_Startup.py