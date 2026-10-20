#!/bin/sh
# Explicit opt-in isolated setup. Never called by ordinary workflow entry/adoption.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ "$#" -ne 3 ] || [ "$1" != --prefix ] || [ "$3" != --allow-network ]; then
  echo 'usage: install-workflow.sh --prefix NEW_ISOLATED_DIRECTORY --allow-network' >&2
  echo 'Explicit install/network permission required; no changes made.' >&2
  exit 2
fi
PREFIX=$2
case "$PREFIX" in /*) ;; *) echo 'prefix must be absolute' >&2; exit 2;; esac
if [ -e "$PREFIX" ] || [ -L "$PREFIX" ]; then
  echo 'existing/foreign prefix preserved; select a new isolated directory' >&2; exit 2
fi
python3 -m venv "$PREFIX"
"$PREFIX/bin/python" -m pip install --require-hashes -r "$ROOT/runtime/requirements.lock"
"$PREFIX/bin/python" -m pip install 'setuptools==82.0.1' 'wheel==0.46.3' 'packaging==26.3'
"$PREFIX/bin/python" -m pip install --no-deps --no-build-isolation "$ROOT/runtime"
HOST=$("$PREFIX/bin/python" -c 'from coherence_workflow.pi_adapter import host_path; print(host_path().parent)')
npm ci --prefix "$HOST" --cache "$PREFIX/npm-cache" --ignore-scripts
printf 'Isolated workflow ready: %s/bin/coordinate-implementation\nUse explicit --project, --tasks and --executor; no global activation.\n' "$PREFIX"
