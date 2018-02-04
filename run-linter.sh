#!/bin/bash -e

pylint resources/connect service.py plugin.py
pylint --disable=duplicate-code,relative-import,invalid-name,protected-access tests/
