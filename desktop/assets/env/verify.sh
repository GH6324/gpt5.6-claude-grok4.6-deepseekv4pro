#!/bin/bash
set -euo pipefail
py="${COLDBREW_PYTHON:-}"
if [[ -z "$py" ]]; then
  if command -v python3 >/dev/null 2>&1; then py="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then py="$(command -v python)"
  else
    echo "本机没有 python3。" >&2
    exit 1
  fi
fi
"$py" -c "import androguard, pefile, capstone, lief, elftools; print('COLDBREW_ENV_VERIFY_OK')"
