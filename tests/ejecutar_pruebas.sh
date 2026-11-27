#!/usr/bin/env bash
# Ejecuta tests/pruebas.http sobre una base SQLite aislada y temporal.
# Requisitos: uv, Node.js/npx, curl.
#
# Uso:
#   bash tests/ejecutar_pruebas.sh
#   PUERTO=8099 bash tests/ejecutar_pruebas.sh

set -euo pipefail
export MSYS_NO_PATHCONV=1

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

DIR_EVIDENCIA="$RAIZ/tests/evidencia"
mkdir -p "$DIR_EVIDENCIA"
MARCA="$(date +%Y%m%d-%H%M%S)"
LOG="$DIR_EVIDENCIA/ejecucion-${MARCA}.log"
LOG_API="$DIR_EVIDENCIA/uvicorn-${MARCA}.log"

if ! command -v npx >/dev/null 2>&1; then
  echo "ERROR: se requiere Node.js/npx para ejecutar httpyac." | tee "$LOG"
  exit 1
fi

{
  echo "Fecha: $(date -Iseconds)"
  echo
} | tee "$LOG"

PYTHON="$RAIZ/.venv/bin/python"
if [[ -d "$RAIZ/.venv/Scripts" ]]; then
  PYTHON="$RAIZ/.venv/Scripts/python.exe"
fi

if command -v uv >/dev/null 2>&1; then
  uv sync --quiet 2>&1 | tee -a "$LOG"
fi

if [[ -z "${PUERTO:-}" ]]; then
  PUERTO="$("$PYTHON" - <<'PY'
import socket
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    print(s.getsockname()[1])
PY
)"
fi
PUERTO="${PUERTO//$'\r'/}"

BASE_URL="http://127.0.0.1:${PUERTO}"
DB="$(mktemp /tmp/minimarket_pruebas_XXXXXX.db)"
export DATABASE_URL="sqlite:///${DB}"

ejecutar_con_bd() {
  local modulo="$1"
  shift
  "$PYTHON" -c 'import os,sys,runpy; os.environ["DATABASE_URL"]=sys.argv[1]; modulo=sys.argv[2]; sys.argv=[modulo]+sys.argv[3:]; runpy.run_module(modulo, run_name="__main__")' "$DATABASE_URL" "$modulo" "$@"
}

PID=""
limpiar() {
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  rm -f "$DB"
}
trap limpiar EXIT INT TERM

{
  echo "Base de datos aislada: $DB"
  echo "URL base: $BASE_URL"
  echo
} | tee -a "$LOG"

ejecutar_con_bd alembic upgrade head 2>&1 | tee -a "$LOG"

ejecutar_con_bd uvicorn app.main:app --host 127.0.0.1 --port "$PUERTO" >"$LOG_API" 2>&1 &
PID=$!

for _ in $(seq 1 60); do
  if "$PYTHON" -c 'import sys,urllib.request; urllib.request.urlopen(sys.argv[1], timeout=1).close()' "$BASE_URL/openapi.json" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! "$PYTHON" -c 'import sys,urllib.request; urllib.request.urlopen(sys.argv[1], timeout=1).close()' "$BASE_URL/openapi.json" >/dev/null 2>&1; then
  echo "ERROR: la API no arrancó. Revisa $LOG_API" | tee -a "$LOG"
  exit 1
fi

set +e
npx --yes httpyac send tests/pruebas.http --all --no-color --var baseUrl="$BASE_URL" 2>&1 | tee -a "$LOG"
ESTADO=${PIPESTATUS[0]}
set -e

{
  echo
  if [[ "$ESTADO" -eq 0 ]]; then
    echo "RESULTADO: todas las pruebas pasaron."
  else
    echo "RESULTADO: hubo pruebas fallidas (código $ESTADO)."
  fi
  echo "Log guardado en: $LOG"
} | tee -a "$LOG"

exit "$ESTADO"
