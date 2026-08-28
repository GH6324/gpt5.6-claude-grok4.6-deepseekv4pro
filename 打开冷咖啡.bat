@echo off
chcp 65001 >nul
cd /d "%~dp0desktop"
where node >nul 2>nul
if errorlevel 1 (
  echo 需要 Node.js。先装 https://nodejs.org
  pause
  exit /b 1
)
if not exist "node_modules\electron" (
  echo 正在安装 Electron ...
  call npm install
  if errorlevel 1 (
    echo npm install 失败。
    pause
    exit /b 1
  )
)
npx electron .
