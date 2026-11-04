#!/bin/sh
# Explicit opt-in isolated setup. Never called by ordinary workflow entry/adoption.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if { [ "$#" -ne 3 ] && [ "$#" -ne 4 ]; } || [ "${1:-}" != --prefix ] || [ "${3:-}" != --allow-network ] ||
   { [ "$#" -eq 4 ] && [ "$4" != --global ]; }; then
  echo 'usage: install-workflow.sh --prefix NEW_ISOLATED_DIRECTORY --allow-network [--global]' >&2
  echo 'Explicit install/network permission required; no changes made.' >&2
  exit 2
fi
PREFIX=$2
case "$PREFIX" in /*) ;; *) echo 'prefix must be absolute' >&2; exit 2;; esac
if [ -e "$PREFIX" ] || [ -L "$PREFIX" ]; then
  echo 'existing/foreign prefix preserved; select a new isolated directory' >&2; exit 2
fi
# Explicit global activation adds links only; preserve foreign destinations.
BIN="$HOME/.local/bin/coordinate-implementation"
EXTENSION="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/extensions/coordinate-implementation-bridge.js"
check_link() {
  if [ -e "$1" ] || [ -L "$1" ]; then
    if [ ! -L "$1" ] || [ "$(readlink "$1")" != "$2" ]; then
      echo "existing/foreign destination preserved: $1; resolve it before global installation" >&2
      exit 2
    fi
  fi
}
if [ "$#" -eq 4 ]; then
  check_link "$BIN" "$PREFIX/bin/coordinate-implementation"
  check_link "$EXTENSION" "$ROOT/runtime/pi-extensions/coordinate-implementation-bridge.js"
fi
python3 -m venv "$PREFIX"
"$PREFIX/bin/python" -m pip install --require-hashes -r "$ROOT/runtime/requirements.lock"
"$PREFIX/bin/python" -m pip install 'setuptools==82.0.1' 'wheel==0.46.3' 'packaging==26.3'
"$PREFIX/bin/python" -m pip install --no-deps --no-build-isolation "$ROOT/runtime"
HOST=$("$PREFIX/bin/python" -c 'from coherence_workflow.pi_adapter import host_path; print(host_path().parent)')
npm ci --prefix "$HOST" --cache "$PREFIX/npm-cache" --ignore-scripts
printf 'Isolated workflow ready: %s/bin/coordinate-implementation\n' "$PREFIX"
if [ "$#" -eq 4 ]; then
  check_link "$BIN" "$PREFIX/bin/coordinate-implementation"
  check_link "$EXTENSION" "$ROOT/runtime/pi-extensions/coordinate-implementation-bridge.js"
  mkdir -p "$(dirname "$BIN")" "$(dirname "$EXTENSION")"
  [ -L "$BIN" ] || ln -s "$PREFIX/bin/coordinate-implementation" "$BIN"
  [ -L "$EXTENSION" ] || ln -s "$ROOT/runtime/pi-extensions/coordinate-implementation-bridge.js" "$EXTENSION"
  printf 'Global command: %s\nGlobal Pi bridge: %s\nKeep this suite checkout. Ensure ~/.local/bin is on PATH; use a fresh Pi/Paseo session.\n' "$BIN" "$EXTENSION"
else
  printf 'Use explicit --project, --tasks and --executor; no global activation.\n'
fi
