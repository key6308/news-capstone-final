#!/usr/bin/env sh
set -eu
python -m sphinx -b html docs docs/_build/html
printf 'Documentation built at docs/_build/html/index.html\n'
