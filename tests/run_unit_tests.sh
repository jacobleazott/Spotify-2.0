#!/bin/bash

export PYTHONPATH=$(pwd)/src:$PYTHONPATH
source .venv/bin/activate
python3 tests/Playback_Macro_Tests.py
python3 tests/test_General_Spotify_Helper.py