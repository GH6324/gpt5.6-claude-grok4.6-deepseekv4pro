#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "需要 Node.js。先装 https://nodejs.org 或 brew install node"
  exit 1
fi
if [[ ! -d node_modules/electron ]]; then
  echo "正在安装 Electron ..."
  npm install
fi
npx electron .
