#!/usr/bin/env bash
set -euo pipefail

# Advanced startup script for DividaFácil (Bash)
# Features:
#  - Modes: all (default), backend, frontend, dev, prod, test, lint
#  - Dependency caching (Python + Node) via SHA256 hashes
#  - Python virtualenv auto-management (.venv)
#  - Optional skip install (--skip-install) & skip build (--no-build)
#  - .env loading
#  - Optional fixtures population (--fixtures)
#  - Prefixed logs for backend/frontend
#  - Test mode: ephemeral SQLite DB + pytest + cleanup
#  - Lint mode: black, isort, ruff checks
#
# Usage examples:
#   ./start-app.sh                 # backend (reload) + frontend dev (same as dev)
#   ./start-app.sh prod            # production style (build + backend only)
#   ./start-app.sh test            # isolated tests
#   ./start-app.sh backend --fixtures
#   ./start-app.sh lint

MODE="all"
NO_BUILD=0
FIXTURES=0
HOST="127.0.0.1"
PORT=8000
ENV_FILE=".env"
SKIP_INSTALL=0

print_help() {
  cat <<EOF
Uso: $0 [modo] [opções]
Modos: all (padrão), backend, frontend, dev, prod, test, lint
Opções:
  --no-build        Não executar build do frontend (quando aplicável)
  --fixtures        Popular dados de teste (create_test_data.py)
  --env-file FILE   Especificar arquivo .env (padrão .env)
  --host HOST       Host backend (default 127.0.0.1)
  --port PORT       Porta backend (default 8000)
  --skip-install    Pular instalação de dependências
  -h, --help        Mostrar ajuda
Exemplos:
  $0 dev --fixtures
  $0 prod --no-build
  $0 test --port 8100
EOF
}

first_arg="${1:-}" || true
case "$first_arg" in
  all|backend|frontend|dev|prod|test|lint)
    MODE="$1"; shift || true ;;
esac

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build) NO_BUILD=1; shift ;;
    --fixtures) FIXTURES=1; shift ;;
    --env-file) ENV_FILE="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    -h|--help) print_help; exit 0 ;;
    *) echo "[ERROR] Opção desconhecida: $1"; print_help; exit 1 ;;
  esac
done

info() { printf '\033[36m[INFO ]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[WARN ]\033[0m %s\n' "$*"; }
err()  { printf '\033[31m[ERROR]\033[0m %s\n' "$*"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

CACHE_DIR="${REPO_ROOT}/.cache"
mkdir -p "$CACHE_DIR"

# --------------- .env LOADING ---------------
load_dotenv() {
  local file="$1"
  [[ -f "$file" ]] || { warn ".env '$file' não encontrado"; return 0; }
  info "Carregando variáveis de $file"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"          # remove trailing comments
    line="$(echo "$line" | xargs)" # trim
    [[ -z "$line" ]] && continue
    if [[ "$line" == *'='* ]]; then
      key="${line%%=*}"; val="${line#*=}"; key="$(echo "$key" | xargs)"; val="$(echo "$val" | xargs)"
      val="${val%\r}"; val="${val%\n}";
      if [[ -z "${!key:-}" ]]; then export "$key"="$val"; fi
    fi
  done < "$file"
}

load_dotenv "$ENV_FILE"

# --------------- PYTHON ENV & DEPS ---------------
if [[ ! -d .venv ]]; then
  info 'Criando virtualenv (.venv)'
  python -m venv .venv
fi
VENV_PY=".venv/bin/python"
[[ "$(uname -s)" == *MINGW* || "$(uname -s)" == *MSYS* || "$(uname -s)" == *CYGWIN* ]] && VENV_PY=".venv/Scripts/python.exe"

file_sha256() { [[ -f "$1" ]] && sha256sum "$1" | awk '{print $1}' || echo ""; }

ensure_python_deps() {
  [[ $SKIP_INSTALL -eq 1 ]] && { warn 'Pulando instalação Python (--skip-install)'; return; }
  [[ -f requirements.txt ]] || { warn 'requirements.txt não encontrado'; return; }
  local hash_file="${CACHE_DIR}/requirements.sha256"
  local current cached
  current="$(file_sha256 requirements.txt)"
  [[ -f "$hash_file" ]] && cached="$(cat "$hash_file")" || cached=""
  if [[ "$current" != "$cached" || ! -d .venv/lib* ]]; then
    info 'Instalando dependências Python'
    "$VENV_PY" -m pip install --upgrade pip wheel >/dev/null
    "$VENV_PY" -m pip install -r requirements.txt
    echo "$current" > "$hash_file"
  else
    info 'Dependências Python em cache'
  fi
}

# --------------- NODE DEPS ---------------
ensure_node_deps() {
  [[ -f frontend/package.json ]] || { warn 'frontend/package.json não encontrado'; return; }
  [[ $SKIP_INSTALL -eq 1 ]] && { warn 'Pulando instalação Node (--skip-install)'; return; }
  local lock="frontend/package-lock.json"
  local hash_file="${CACHE_DIR}/frontend_deps.sha256"
  local current cached
  if [[ -f "$lock" ]]; then current="$(file_sha256 "$lock")"; else current="$(file_sha256 frontend/package.json)"; fi
  [[ -f "$hash_file" ]] && cached="$(cat "$hash_file")" || cached=""
  if [[ "$current" != "$cached" || ! -d frontend/node_modules ]]; then
    info 'Instalando dependências frontend (npm ci/install)'
    pushd frontend >/dev/null
    if [[ -f package-lock.json ]]; then npm ci; else npm install; fi
    popd >/dev/null
    echo "$current" > "$hash_file"
  else
    info 'Dependências frontend em cache'
  fi
}

# --------------- FIXTURES ---------------
load_fixtures() {
  [[ $FIXTURES -eq 1 ]] || return 0
  if [[ ! -f create_test_data.py && -f scripts/create_test_data.py ]]; then cp scripts/create_test_data.py create_test_data.py; fi
  [[ -f create_test_data.py ]] || { warn 'create_test_data.py não encontrado'; return; }
  info 'Populando dados de teste (fixtures)'
  "$VENV_PY" create_test_data.py || warn 'Falha ao carregar fixtures'
}

# --------------- LINT ---------------
run_lint() {
  ensure_python_deps
  info 'Executando linters (black/isort/ruff)'
  "$VENV_PY" -m pip install -q black isort ruff
  "$VENV_PY" -m black --check .
  "$VENV_PY" -m isort --check-only .
  "$VENV_PY" -m ruff check .
}

# --------------- BACKEND ---------------
start_backend() {
  local reload_flag="$1"; local db_url="$2"; local listen_port="$3"
  ensure_python_deps
  [[ -n "$db_url" ]] && export DATABASE_URL="$db_url"
  info "Iniciando backend (porta $listen_port)"
  if [[ "$reload_flag" == "reload" ]]; then
    "$VENV_PY" -m uvicorn web_app:app --host "$HOST" --port "$listen_port" --reload 2>&1 | sed -u 's/^/[BACKEND] /'
  else
    "$VENV_PY" -m uvicorn web_app:app --host "$HOST" --port "$listen_port" 2>&1 | sed -u 's/^/[BACKEND] /'
  fi
}

start_backend_async() {
  local reload_flag="$1"; local db_url="$2"; local listen_port="$3"
  ( start_backend "$reload_flag" "$db_url" "$listen_port" ) &
  BACKEND_PID=$!
}

# --------------- FRONTEND ---------------
build_frontend() {
  ensure_node_deps
  if [[ $NO_BUILD -eq 1 ]]; then warn '--no-build ativo: pulando build'; return; fi
  info 'Build frontend'
  pushd frontend >/dev/null
  npm run build >/dev/null
  popd >/dev/null
}

dev_frontend() {
  ensure_node_deps
  info 'Iniciando frontend dev (vite)'
  pushd frontend >/dev/null
  npm run dev 2>&1 | sed -u 's/^/[FRONTEND] /'
  popd >/dev/null
}

dev_frontend_async() {
  ( dev_frontend ) &
  FRONTEND_PID=$!
}

# --------------- TEST MODE ---------------
run_tests_isolated() {
  ensure_python_deps
  local test_db="test.db"
  [[ -f "$test_db" ]] && rm -f "$test_db"
  local test_port=$PORT
  [[ $test_port -eq 8000 ]] && test_port=8100
  info "Modo test: DB=$test_db porta=$test_port"
  start_backend_async reload "sqlite:///./$test_db" "$test_port"
  # wait health
  local health="http://$HOST:$test_port/healthz"
  local max=40
  for ((i=0;i<max;i++)); do
    if curl -fsS "$health" >/dev/null 2>&1; then break; fi
    sleep 0.3
  done
  if ! curl -fsS "$health" >/dev/null 2>&1; then
    err 'Backend não ficou saudável a tempo'
    kill "$BACKEND_PID" 2>/dev/null || true
    exit 1
  fi
  info 'Executando pytest'
  "$VENV_PY" -m pytest -q || TEST_CODE=$? || true
  TEST_CODE=${TEST_CODE:-0}
  info 'Encerrando backend de teste'
  kill "$BACKEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
  rm -f "$test_db"
  exit "$TEST_CODE"
}

# --------------- DISPATCH ---------------
trap '[[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true; [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true' EXIT INT TERM

case "$MODE" in
  lint)
    run_lint; exit 0 ;;
  test)
    run_tests_isolated ;;
  prod)
    build_frontend
    [[ $FIXTURES -eq 1 ]] && load_fixtures
    start_backend no-reload "" "$PORT" ;;
  backend)
    [[ $FIXTURES -eq 1 ]] && load_fixtures
    start_backend reload "" "$PORT" ;;
  frontend)
    dev_frontend ;;
  dev|all)
    [[ $FIXTURES -eq 1 ]] && load_fixtures
    info 'Modo desenvolvimento (backend + frontend)'
    start_backend_async reload "" "$PORT"
    sleep 1
    dev_frontend
    ;;
  *)
    err "Modo desconhecido: $MODE"; exit 1 ;;
esac
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="all"
PORT=8000
FRONTEND_PORT=3000
NO_BUILD=false

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to start backend
start_backend() {
    print_color "$BLUE" "🚀 Starting Backend Server..."
    
    # Check if Python is available
    if ! command_exists python && ! command_exists python3; then
        print_color "$RED" "❌ Python not found. Please install Python 3.12+ and ensure it's in your PATH."
        exit 1
    fi
    
    # Use python3 if available, otherwise python
    PYTHON_CMD="python3"
    if ! command_exists python3; then
        PYTHON_CMD="python"
    fi
    
    # Change to backend directory
    cd backend || exit 1
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_color "$YELLOW" "📦 Creating Python virtual environment..."
        $PYTHON_CMD -m venv .venv
    fi
    
    # Activate virtual environment
    print_color "$YELLOW" "🔧 Activating virtual environment..."
    source .venv/bin/activate
    
    # Install dependencies
    print_color "$YELLOW" "📦 Installing/updating Python dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start the backend server
    print_color "$GREEN" "🌐 Starting FastAPI backend on http://localhost:${PORT}"
    python -m uvicorn web_app:app --host 127.0.0.1 --port "$PORT" --reload
}

# Function to start frontend
start_frontend() {
    print_color "$BLUE" "🚀 Starting Frontend Server..."
    
    # Check if Node.js is available
    if ! command_exists node; then
        print_color "$RED" "❌ Node.js not found. Please install Node.js and npm."
        exit 1
    fi
    
    # Change to frontend directory
    cd frontend || exit 1
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_color "$YELLOW" "📦 Installing npm dependencies..."
        npm install
    fi
    
    # Build frontend if not skipped
    if [ "$NO_BUILD" != true ]; then
        print_color "$YELLOW" "🔨 Building frontend..."
        npm run build
    fi
    
    # Start the frontend server
    print_color "$GREEN" "🌐 Starting React frontend on http://localhost:${FRONTEND_PORT}"
    PORT="$FRONTEND_PORT" npm start
}

# Function to start both
start_all() {
    print_color "$BLUE" "🚀 Starting DividaFácil Application..."
    print_color "$YELLOW" "This will start both backend and frontend servers."
    print_color "$YELLOW" "Backend: http://localhost:${PORT}"
    print_color "$YELLOW" "Frontend: http://localhost:${FRONTEND_PORT}"
    echo ""
    
    # Start backend in background
    print_color "$YELLOW" "🔄 Starting backend in background..."
    (cd backend && source .venv/bin/activate && python -m uvicorn web_app:app --host 127.0.0.1 --port "$PORT" --reload) &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if curl -s "http://localhost:${PORT}/healthz" > /dev/null; then
        print_color "$GREEN" "✅ Backend started successfully!"
    else
        print_color "$YELLOW" "⚠️  Backend might still be starting..."
    fi
    
    # Start frontend (this will run in foreground)
    start_frontend
    
    # Kill backend when script exits
    trap "kill $BACKEND_PID 2>/dev/null" EXIT
}

# Function to show help
show_help() {
    echo "DividaFácil Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --mode MODE       Specify which part to start: all (default), backend, frontend"
    echo "  -p, --port PORT       Backend port (default: 8000)"
    echo "  -f, --frontend-port   Frontend port (default: 3000)"
    echo "  -n, --no-build        Skip building the frontend"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    Start both frontend and backend"
    echo "  $0 -m backend         Start only backend"
    echo "  $0 -m frontend -n     Start only frontend without building"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -f|--frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -n|--no-build)
            NO_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate mode
if [[ ! "$MODE" =~ ^(all|backend|frontend)$ ]]; then
    print_color "$RED" "❌ Invalid mode: $MODE. Must be 'all', 'backend', or 'frontend'"
    exit 1
fi

# Main execution
print_color "$BLUE" "🎯 DividaFácil Startup Script"
print_color "$BLUE" "=============================="

case $MODE in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_all
        ;;
esac