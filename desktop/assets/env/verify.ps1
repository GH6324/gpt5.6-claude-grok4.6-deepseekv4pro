$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw '本机没有 python。' }
& $python.Source -c "import androguard, pefile, capstone, lief, elftools; print('COLDBREW_ENV_VERIFY_OK')"
if ($LASTEXITCODE -ne 0) { throw "环境校验失败，退出码 $LASTEXITCODE" }
