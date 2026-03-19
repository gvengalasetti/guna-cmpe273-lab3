#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="python3"
VENV_DIR=".venv"
PIDS=()

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done
}

trap cleanup EXIT

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python3 is required"
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "Starting registry on :8500"
python registry.py > registry.log 2>&1 &
PIDS+=("$!")

sleep 1

echo "Starting service instance A on :9001"
python service_instance.py --instance-id service-a --port 9001 > service-a.log 2>&1 &
PIDS+=("$!")

echo "Starting service instance B on :9002"
python service_instance.py --instance-id service-b --port 9002 > service-b.log 2>&1 &
PIDS+=("$!")

sleep 2

echo
echo "Running client with random instance selection"
python client.py --calls 8 --delay-seconds 0.4

echo
echo "Demo complete"
echo "- Registry log: $SCRIPT_DIR/registry.log"
echo "- Service A log: $SCRIPT_DIR/service-a.log"
echo "- Service B log: $SCRIPT_DIR/service-b.log"