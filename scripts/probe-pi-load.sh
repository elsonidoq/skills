#!/usr/bin/env bash
# Minimal probe: start pi headless once and confirm the skill suite loads without
# warnings or collisions. Costs exactly one cheap model call.
# Usage: scripts/probe-pi-load.sh [model] [skills-dir]
set -u
MODEL="${1:-deepseek/deepseek-v4.1-flash}"
INFIX="${2:-}"
PROMPT='Reply with exactly: OK'
tmp=$(mktemp)
trap 'rm -f "$tmp" "$tmp.err"' EXIT

if [ -n "$INFIX" ]; then
  if [ -f "$INFIX" ]; then PROMPT="$PROMPT $INFIX"; else PROMPT="$PROMPT $INFIX"; fi
fi

pi -p --no-session --model "$MODEL" "$PROMPT" >"$tmp" 2>"$tmp.err"
rc=$?

echo "exit=$rc"
echo "--- stderr diagnostics ---"
cat "$tmp.err"
echo "--- stdout ---"
cat "$tmp"

# Fail on skill-loading diagnostic patterns.
if grep -Eiq 'skill.*(warn|collision|invalid|fail)|(warn|collision|invalid).*skill' "$tmp.err"; then
  echo "PROBE-FAIL: skill diagnostics present on stderr"; exit 1
fi
if ! grep -qx 'OK' "$tmp"; then
  echo "PROBE-FAIL: expected exactly 'OK'"; exit 1
fi
[ "$rc" -eq 0 ] || { echo "PROBE-FAIL: nonzero exit"; exit 1; }
echo "PROBE-OK"