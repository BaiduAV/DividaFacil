<#
Advanced startup script for DividaFácil (PowerShell)
Features:
  - Modes: all (default), backend, frontend, dev, prod, test, lint
  - Dependency caching (Python + Node) via file hashes
  - Virtual environment auto-management (.venv)
  - Optional skip install (--SkipInstall) and skip build (--NoBuild)
  - .env loading
  - Optional fixtures population (--Fixtures)  
  - Prefixed streaming logs for backend/frontend
  - Test mode: ephemeral SQLite DB + pytest + cleanup
  - Lint mode: black, isort, ruff checks
Usage examples:
  ./start-app.ps1              # start both (dev style: backend reload + frontend dev)
  ./start-app.ps1 -Mode prod   # build frontend & serve via backend only
  ./start-app.ps1 -Mode test   # run isolated tests
  ./start-app.ps1 -Mode backend -Fixtures
  ./start-app.ps1 -Mode lint
#>

param(
  [ValidateSet('all','backend','frontend','dev','prod','test','lint')]
  [string]$Mode = 'all',
  [switch]$NoBuild,
  [switch]$Fixtures,
  [string]$HostAddress = '127.0.0.1',
  [int]$Port = 8000,
  [string]$EnvFile = '.env',
  [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO ] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN ] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$CacheDir = Join-Path $RepoRoot '.cache'
if (-not (Test-Path $CacheDir)) { New-Item -ItemType Directory -Path $CacheDir | Out-Null }

# --------------------- ENV LOADING ---------------------
function Load-DotEnv {
  param([string]$Path)
  if (-not (Test-Path $Path)) { Write-Warn ".env file '$Path' não encontrado (ignorando)."; return }
  Write-Info "Carregando variáveis de $Path"
  Get-Content $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    if ($line.StartsWith('#')) { return }
    $kv = $line -split '=',2
    if ($kv.Count -ne 2) { return }
    $key = $kv[0].Trim()
    $val = $kv[1].Trim().Trim('"').Trim("'")
    if (-not [string]::IsNullOrWhiteSpace($key)) {
      if (-not (Get-Item "Env:$key" -ErrorAction SilentlyContinue)) { Set-Item "Env:$key" $val }
    }
  }
}

Load-DotEnv -Path $EnvFile

# --------------------- PYTHON ENV & DEPS ---------------------
$VenvPy = if ([System.Environment]::OSVersion.Platform -eq 'Win32NT') { Join-Path $RepoRoot '.venv/Scripts/python.exe' } else { Join-Path $RepoRoot '.venv/bin/python' }
if (-not (Test-Path $VenvPy)) {
  Write-Info 'Criando virtualenv (.venv)'
  python -m venv .venv
}

function Get-FileSha256($path) {
  if (-not (Test-Path $path)) { return '' }
  return (Get-FileHash -Algorithm SHA256 -Path $path).Hash
}

function Ensure-PythonDependencies {
  if ($SkipInstall) { Write-Warn 'Pulando instalação de dependências Python (--SkipInstall).'; return }
  if (-not (Test-Path 'backend/requirements.txt')) { Write-Warn 'backend/requirements.txt não encontrado'; return }
  $hashFile = Join-Path $CacheDir 'requirements.sha256'
  $current = Get-FileSha256 'backend/requirements.txt'
  $cached  = if (Test-Path $hashFile) { Get-Content $hashFile -ErrorAction SilentlyContinue } else { '' }
  if ($current -ne $cached -or -not (Test-Path 'backend/.venv/Lib') ) {
    Write-Info 'Instalando dependências Python (alteração detectada ou primeira vez)'
    Set-Location backend
    & $VenvPy -m pip install --upgrade pip wheel > $null
    & $VenvPy -m pip install -r requirements.txt
    Set-Location ..
    $current | Out-File $hashFile -Encoding ascii -Force
  } else {
    Write-Info 'Dependências Python em cache - nada a fazer.'
  }
}

# --------------------- NODE DEPS ---------------------
function Ensure-NodeDependencies {
  if (-not (Test-Path 'frontend/package.json')) { Write-Warn 'frontend/package.json não encontrado; pulando parte frontend.'; return }
  if ($SkipInstall) { Write-Warn 'Pulando instalação de dependências Node (--SkipInstall).'; return }
  $lockFile = 'frontend/package-lock.json'
  $hashFile = Join-Path $CacheDir 'frontend_deps.sha256'
  $current = Get-FileSha256 $lockFile
  if (-not $current) { $current = Get-FileSha256 'frontend/package.json' }
  $cached = if (Test-Path $hashFile) { Get-Content $hashFile -ErrorAction SilentlyContinue } else { '' }
  if ($current -ne $cached -or -not (Test-Path 'frontend/node_modules')) {
    Write-Info 'Instalando dependências frontend (npm ci)'
    push-location frontend
    if (Test-Path package-lock.json) { npm ci } else { npm install }
    pop-location
    $current | Out-File $hashFile -Encoding ascii -Force
  } else {
    Write-Info 'Dependências frontend em cache - nada a fazer.'
  }
}

# --------------------- FIXTURES ---------------------
function Load-Fixtures {
  if (-not $Fixtures) { return }
  if (-not (Test-Path 'backend/create_test_data.py')) { 
    if (Test-Path 'backend/scripts/create_test_data.py') { 
      Copy-Item 'backend/scripts/create_test_data.py' 'backend/create_test_data.py' 
    } 
  }
  if (-not (Test-Path 'backend/create_test_data.py')) { Write-Warn 'create_test_data.py não encontrado'; return }
  Write-Info 'Populando dados de teste (fixtures)'
  Set-Location backend
  & $VenvPy create_test_data.py
  Set-Location ..
}

# --------------------- LINT ---------------------
function Run-Lint {
  Ensure-PythonDependencies
  Write-Info 'Executando linters (black/isort/ruff)'
  Set-Location backend
  & $VenvPy -m pip install -q black isort ruff
  & $VenvPy -m black --check .
  & $VenvPy -m isort --check-only .
  & $VenvPy -m ruff check .
  Set-Location ..
}

# --------------------- BACKEND ---------------------
function Start-Backend {
  param([switch]$Reload,[string]$DatabaseUrl,[int]$ListenPort)
  Ensure-PythonDependencies
  if ($DatabaseUrl) { $Env:DATABASE_URL = $DatabaseUrl }
  $reloadArg = if ($Reload) { '--reload' } else { '' }
  Write-Info "Iniciando backend (porta $ListenPort)"
  Set-Location backend
  # Stream logs with prefix
  & $VenvPy -m uvicorn web_app:app --host $HostAddress --port $ListenPort $reloadArg 2>&1 | ForEach-Object { Write-Host "[BACKEND] $_" }
  Set-Location ..
}

function Start-Backend-Async {
  param([switch]$Reload,[string]$DatabaseUrl,[int]$ListenPort)
  Start-Job -ScriptBlock {
    param($RepoRoot,$HostAddress,$ListenPort,$Reload,$DatabaseUrl)
    Set-Location (Join-Path $RepoRoot 'backend')
    $VenvPy = if ([System.Environment]::OSVersion.Platform -eq 'Win32NT') { Join-Path $RepoRoot '.venv/Scripts/python.exe' } else { Join-Path $RepoRoot '.venv/bin/python' }
    if ($DatabaseUrl) { $Env:DATABASE_URL = $DatabaseUrl }
    $reloadArg = if ($Reload) { '--reload' } else { '' }
    & $VenvPy -m uvicorn web_app:app --host $HostAddress --port $ListenPort $reloadArg 2>&1 | ForEach-Object { "[BACKEND] $_" }
  } -ArgumentList $RepoRoot,$HostAddress,$Port,$Reload,$DatabaseUrl | Out-Null
}

# --------------------- FRONTEND ---------------------
function Build-Frontend {
  Ensure-NodeDependencies
  if ($NoBuild) { Write-Warn 'Flag --NoBuild ativa: pulando build frontend.'; return }
  Write-Info 'Build frontend (npm run build)'
  push-location frontend
  npm run build --silent
  pop-location
}

function Dev-Frontend {
  Ensure-NodeDependencies
  Write-Info 'Iniciando frontend dev server (npm run dev)'
  push-location frontend
  npm run dev 2>&1 | ForEach-Object { Write-Host "[FRONTEND] $_" }
  pop-location
}

function Dev-Frontend-Async {
  Start-Job -ScriptBlock {
    param($RepoRoot)
    Set-Location (Join-Path $RepoRoot 'frontend')
    npm run dev 2>&1 | ForEach-Object { "[FRONTEND] $_" }
  } -ArgumentList $RepoRoot | Out-Null
}

# --------------------- TEST MODE ---------------------
function Run-Tests-Isolated {
  Ensure-PythonDependencies
  $testDb = 'backend/test.db'
  if (Test-Path $testDb) { Remove-Item $testDb -Force }
  $testPort = if ($Port -eq 8000) { 8100 } else { $Port }
  Write-Info "Modo test: usando DB $testDb e porta $testPort"
  Start-Backend-Async -Reload -DatabaseUrl "sqlite:///./test.db" -ListenPort $testPort
  # Aguarda saúde
  $healthUrl = "http://${HostAddress}:$testPort/healthz"
  $max = 30; $ok = $false
  for ($i=0; $i -lt $max; $i++) {
    Start-Sleep -Milliseconds 400
    try {
      $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2
      if ($resp.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
  }
  if (-not $ok) { Write-Err 'Backend não ficou saudável a tempo.'; Get-Job | Remove-Job -Force; exit 1 }
  Write-Info 'Executando pytest'
  Set-Location backend
  & $VenvPy -m pytest -q
  $code = $LASTEXITCODE
  Set-Location ..
  Write-Info 'Encerrando backend de teste'
  Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
  if (Test-Path $testDb) { Remove-Item $testDb -Force }
  exit $code
}

# --------------------- DISPATCH ---------------------
switch ($Mode) {
  'lint' { Run-Lint; exit 0 }
  'test' { Run-Tests-Isolated }
}

if ($Mode -in @('prod')) {
  # Production style: build once, serve via backend only (no reload, static served by backend)
  Build-Frontend
  if ($Fixtures) { Load-Fixtures }
  Start-Backend -Reload:$false -ListenPort $Port
  exit 0
}

if ($Mode -in @('backend')) {
  if ($Fixtures) { Load-Fixtures }
  Start-Backend -Reload -ListenPort $Port
  exit 0
}

if ($Mode -in @('frontend')) {
  Dev-Frontend
  exit 0
}

if ($Mode -in @('dev','all')) {
  # dev/all: run backend (reload) + frontend dev concurrently
  if ($Fixtures) { Load-Fixtures }
  Write-Info 'Iniciando modo desenvolvimento (backend + frontend)'
  Start-Backend-Async -Reload -ListenPort $Port
  Start-Sleep -Seconds 1
  Dev-Frontend
  Write-Info 'Encerrando jobs'
  Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
  exit 0
}

Write-Err "Modo desconhecido: $Mode"
exit 1