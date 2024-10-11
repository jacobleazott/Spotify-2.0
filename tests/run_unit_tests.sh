#!/bin/bash

export PYTHONPATH=$(pwd)/src:$PYTHONPATH
source .venv/bin/activate
pytest tests "$@"