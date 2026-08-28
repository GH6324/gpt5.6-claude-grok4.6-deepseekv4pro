$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw '本机没有 python。先装 Python 3.10+。' }
$req = Join-Path $here 'requirements-reverse.txt'
& $python.Source -m pip install -r $req
if ($LASTEXITCODE -ne 0) { throw "pip 安装失败，退出码 $LASTEXITCODE" }
Write-Host 'COLDBREW_ENV_OK'
