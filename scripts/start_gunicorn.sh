#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/sr_venv}"

if [[ -x "$VENV_DIR/bin/python" ]]; then
  PYTHON_BIN="$VENV_DIR/bin/python"
elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
  PYTHON_BIN="$VENV_DIR/Scripts/python.exe"
else
  echo "Python executable not found in VENV_DIR=$VENV_DIR" >&2
  exit 1
fi

cd "$ROOT_DIR"
exec "$PYTHON_BIN" -m gunicorn -c "$ROOT_DIR/gunicorn.conf.py"
