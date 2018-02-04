#!/bin/bash -e

export PYTHONPATH="${PYTHONPATH}:/home/python/app/resources/lib:/home/python/app/resources"

python -m unittest discover -s tests/
