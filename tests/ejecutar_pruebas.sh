#!/usr/bin/env bash
# Ejecuta tests/pruebas.http sobre una base SQLite aislada y temporal.
# Requisitos: uv, Node.js/npx, curl.
#
# Uso:
#   bash tests/ejecutar_pruebas.sh
#   PUERTO=8099 bash tests/ejecutar_pruebas.sh

set -euo pipefail

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

uv sync --quiet 2>&1 | tee -a "$LOG"

if [[ -z "${PUERTO:-}" ]]; then
  PUERTO="$("$RAIZ/.venv/bin/python" - <<'PY'
import socket
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    print(s.getsockname()[1])
PY
)"
fi

BASE_URL="http://127.0.0.1:${PUERTO}"
DB="$(mktemp /tmp/minimarket_pruebas_XXXXXX.db)"
export DATABASE_URL="sqlite:///${DB}"

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

.venv/bin/alembic upgrade head 2>&1 | tee -a "$LOG"

.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$PUERTO" >"$LOG_API" 2>&1 &
PID=$!

for _ in $(seq 1 60); do
  if curl -fsS "$BASE_URL/openapi.json" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! curl -fsS "$BASE_URL/openapi.json" >/dev/null 2>&1; then
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
