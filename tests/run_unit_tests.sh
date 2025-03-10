#!/bin/bash

export PYTHONPATH=$(pwd)/src:$(pwd)/tests:$PYTHONPATH
source .venv/bin/activate
coverage run -m pytest --no-header tests "$@"
coverage report --skip-covered --sort=Cover
coverage xml