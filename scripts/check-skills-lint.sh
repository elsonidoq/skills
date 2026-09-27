#!/usr/bin/env bash
# Static lint for the pi skill suite. Deterministic; needs no model.
# Usage: scripts/check-skills-lint.sh [skills-dir]
set -u
SKILLS_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/skills}"
fail=0

FORBIDDEN=(
  '~/.claude'
  '~/.config/opencode'
  'opencode'
  'OpenCode'
  'restart OpenCode'
  'the `question` tool'
  'task tool'
)

check_file() {
  local f="$1" dir name desc len bad
  dir=$(basename "$(dirname "$f")")
  name=$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1)
  desc=$(sed -n 's/^description:[[:space:]]*//p' "$f" | head -1)
  len=${#desc}
  local ok=1
  [ "$name" = "$dir" ] || { echo "FAIL $f: name '$name' != dir '$dir'"; ok=0; }
  if [ -z "$desc" ]; then echo "FAIL $f: missing description"; ok=0;
  else
    [[ "$desc" == "Use when"* ]] || { echo "FAIL $f: description must start with 'Use when...'"; ok=0; }
    [ "$len" -le 1024 ] || { echo "FAIL $f: description $len > 1024 chars"; ok=0; }
  fi
  for bad in "${FORBIDDEN[@]}"; do
    grep -qiF "$bad" "$f" && { echo "FAIL $f: contains '$bad'"; ok=0; }
  done
  [ "$ok" = 1 ] && echo "OK   $f"
  return $((1 - ok))
}

count=0
while IFS= read -r f; do
  count=$((count + 1))
  check_file "$f" || fail=$((fail + 1))
done < <(find "$SKILLS_DIR" -name SKILL.md -type f | sort)

echo "----"
echo "$count skills checked, $fail failed"
[ "$fail" -eq 0 ]