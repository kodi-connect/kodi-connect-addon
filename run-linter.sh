#!/bin/bash -e

pylint resources/connect service.py plugin.py
pylint --disable=duplicate-code,relative-import,invalid-name,protected-access tests/

flake8 --ignore=E402,E302,E305 service.py plugin.py
flake8 resources/connect tests
