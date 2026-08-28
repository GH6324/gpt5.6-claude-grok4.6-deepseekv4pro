#!/bin/bash
cd "$(dirname "$0")/desktop" || exit 1
if ! command -v node >/dev/null 2>&1; then
  osascript -e 'display alert "冷咖啡" message "需要先安装 Node.js：https://nodejs.org 或 brew install node"'
  exit 1
fi
if [[ ! -d node_modules/electron ]]; then
  npm install
fi
npx electron .
