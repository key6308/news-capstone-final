#!/usr/bin/env sh
# Build the Sphinx HTML documentation into docs/_build/html.
#
# Works from any folder. Creates the .venv virtual environment and installs
# requirements.txt automatically if needed, then runs Sphinx with warnings
# treated as errors. Usage:  sh docs/build_docs.sh [--clean]
set -eu

DOCS_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(dirname -- "$DOCS_DIR")
VENV_DIR="$ROOT_DIR/.venv"
BUILD_DIR="$DOCS_DIR/_build"

cd "$ROOT_DIR"

if [ -x "$VENV_DIR/bin/python" ]; then
    PY="$VENV_DIR/bin/python"
elif [ -x "$VENV_DIR/Scripts/python.exe" ]; then
    PY="$VENV_DIR/Scripts/python.exe"
else
    for candidate in python3.12 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            BASE_PY=$candidate
            break
        fi
    done
    if [ -z "${BASE_PY:-}" ]; then
        echo "ERROR: Python 3.12 was not found. Install it and try again." >&2
        exit 1
    fi
    echo "==> Creating virtual environment .venv with $BASE_PY"
    "$BASE_PY" -m venv "$VENV_DIR"
    if [ -x "$VENV_DIR/bin/python" ]; then
        PY="$VENV_DIR/bin/python"
    else
        PY="$VENV_DIR/Scripts/python.exe"
    fi
fi

if ! "$PY" -c 'import sphinx, sphinx_rtd_theme, django, rest_framework, pymysql, requests' 2>/dev/null; then
    echo "==> Installing requirements.txt into .venv"
    "$PY" -m pip install --disable-pip-version-check -r "$ROOT_DIR/requirements.txt"
fi

if [ "${1:-}" = "--clean" ]; then
    rm -rf "$BUILD_DIR/html" "$BUILD_DIR/doctrees"
fi

echo "==> Building HTML documentation with Sphinx"
"$PY" -m sphinx -W --keep-going -b html -d "$BUILD_DIR/doctrees" "$DOCS_DIR" "$BUILD_DIR/html"
printf 'Documentation built at %s\n' "$BUILD_DIR/html/index.html"
