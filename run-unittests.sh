#!/bin/bash -e

export PYTHONPATH="${PYTHONPATH}:/home/python/app/resources/lib:/home/python/app/resources/connect"

python -m unittest discover -s resources/connect/tests/
