#!/bin/bash

export PYTHONPATH=$(pwd)/src:$(pwd)/tests:$PYTHONPATH
source .venv/bin/activate
coverage run -m pytest tests "$@"
coverage report --skip-covered
coverage xml