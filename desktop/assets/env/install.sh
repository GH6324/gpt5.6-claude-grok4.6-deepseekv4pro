#!/bin/bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
py="${COLDBREW_PYTHON:-}"
if [[ -z "$py" ]]; then
  if command -v python3 >/dev/null 2>&1; then py="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then py="$(command -v python)"
  else
    echo "本机没有 python3。先 brew install python。" >&2
    exit 1
  fi
fi
"$py" -m pip install -r "$here/requirements-reverse.txt"
echo COLDBREW_ENV_OK
