#!/bin/bash
# Get the absolute path to the project root (one level up from awr-rag)
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment python not found at $VENV_PYTHON"
    exit 1
fi

echo "Running tests using: $VENV_PYTHON"
export PYTHONPATH=$SCRIPT_DIR
"$VENV_PYTHON" tests/test_chunker.py
