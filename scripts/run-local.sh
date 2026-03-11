#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

CONFIG_PATH="${ECMS_CONFIG_PATH:-config/default.json}"
UI_HOST="${ECMS_UI_HOST:-0.0.0.0}"
UI_PORT="${ECMS_UI_PORT:-8000}"
SCHED_INTERVAL="${ECMS_SCHED_INTERVAL_SECONDS:-0}"
SCHED_MAX_CYCLES="${ECMS_SCHED_MAX_CYCLES:-1}"

echo "[ecms] Starting UI on ${UI_HOST}:${UI_PORT}"
python -m src.ui.app &
UI_PID=$!

cleanup() {
  if kill -0 "$UI_PID" 2>/dev/null; then
    echo "[ecms] Stopping UI (pid=${UI_PID})"
    kill "$UI_PID" || true
  fi
}
trap cleanup EXIT INT TERM

if [[ "$SCHED_INTERVAL" -eq 0 ]]; then
  echo "[ecms] Running scheduler once"
  python -m src.scheduler --config "$CONFIG_PATH"
else
  echo "[ecms] Running scheduler every ${SCHED_INTERVAL}s (max cycles: ${SCHED_MAX_CYCLES})"
  python -m src.scheduler --config "$CONFIG_PATH" --interval-seconds "$SCHED_INTERVAL" --max-cycles "$SCHED_MAX_CYCLES"
fi

echo "[ecms] Scheduler run complete. UI still running; press Ctrl+C to stop."
wait "$UI_PID"
