#!/bin/bash -e

export PYTHONPATH="${PYTHONPATH}:/home/python/app/resources/lib:/home/python/app/resources"

python -m unittest discover -s tests/
DISABLE_NGRAM_INDEX=1 python -m unittest discover -s tests/
