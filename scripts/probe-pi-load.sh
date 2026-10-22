#!/usr/bin/env bash
# End-to-end probe: start pi headless once and assert that (a) no skill
# warnings/collisions appear, and (b) the suite skills are actually advertised
# in the system prompt's <skills> section. Costs exactly one model call.
# Usage: scripts/probe-pi-load.sh [model]
set -uo pipefail
MODEL="${1:-deepseek/deepseek-v4.1-flash}"
SUITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

REQUIRED=(planner tiny-spec coordinate-implementation \
          planning-brainstorming task-generation memory-handling initialize-coherence \
          finish-session writing-skills track-open-issue import-open-issues)

tmp=$(mktemp); tmp2=$(mktemp); trap 'rm -f "$tmp" "$tmp2"' EXIT

pi --mode json --no-session --model "$MODEL" "Reply with exactly: OK" >"$tmp" 2>"$tmp2"
rc=$?

echo "exit=$rc"
echo "--- stderr diagnostics ---"; cat "$tmp2"

if [ "$rc" -ne 0 ]; then echo "PROBE-FAIL: nonzero exit"; exit 1; fi
if grep -Eiq 'skill.*(warn|collision|invalid|fail)|(warn|collision|invalid).*skill' "$tmp2"; then
  echo "PROBE-FAIL: skill diagnostics present on stderr"; exit 1
fi

advertised=$(python3 - "$tmp" <<'PY'
import json, re, sys
names = []
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    try: ev = json.loads(line)
    except Exception: continue
    if ev.get("type") != "message_start": continue
    m = ev.get("message", {})
    if m.get("role") == "system":
        sk = (m.get("sections", {}) or {}).get("skills", "") or ""
        names = re.findall(r"<name>([^<]+)</name>", sk)
        break
print("\n".join(sorted(names)))
PY
)
echo "--- pi advertises ---"
printf '%s\n' "$advertised" | sed 's/^/  - /'
held=$(printf '%s\n' "$advertised")
missing=0
for want in "${REQUIRED[@]}"; do
  if ! printf '%s\n' "$held" | grep -Fxq "$want"; then
    echo "PROBE-FAIL: missing from system prompt: $want"; missing=1
  fi
done
echo "OK"
[ "$missing" -eq 0 ] && echo "PROBE-OK"
exit "$missing"