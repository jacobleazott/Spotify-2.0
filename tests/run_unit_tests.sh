#!/bin/bash

export PYTHONPATH=$(pwd)/src:$(pwd)/tests:$PYTHONPATH
source .venv/bin/activate
pytest tests "$@"