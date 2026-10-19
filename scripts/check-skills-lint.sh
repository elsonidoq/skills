#!/usr/bin/env bash
# Static lint for the pi skill suite. Deterministic; needs no model.
# Usage: scripts/check-skills-lint.sh [skills-dir]
set -u
if [ "${1:-}" = --active-consumers ]; then
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  exec "${COHERENCE_PYTHON:-python3}" "$script_dir/check-planner-workflow.py" --active-consumers
fi
SKILLS_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/skills}"
fail=0
PYTHON="${COHERENCE_PYTHON:-python3}"

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
  # Skip skills whose real path escapes the suite directory (e.g. expert, a
  # symlink maintained in another repository).
  real=$(readlink -f "$f" 2>/dev/null || echo "$f")
  case "$real" in
    "$SKILLS_DIR"/*) ;;
    *) echo "SKIP $f (external)"; continue ;;
  esac
  count=$((count + 1))
  check_file "$f" || fail=$((fail + 1))
done < <(find "$SKILLS_DIR" \( -type f -o -type l \) -name SKILL.md | sort)

echo "----"
echo "$count skills checked, $fail failed"
if [ "$fail" -eq 0 ]; then
  scripts_dir="$(cd "$(dirname "$0")" && pwd)"
  suite_skills="$(cd "$scripts_dir/../skills" && pwd)"
  selected_skills="$(cd "$SKILLS_DIR" && pwd)"
  if [ "$selected_skills" = "$suite_skills" ]; then
    "$PYTHON" "$scripts_dir/check-planner-workflow.py" || fail=$((fail + 1))
    "$PYTHON" "$scripts_dir/check-task-commit-contract.py" || fail=$((fail + 1))
    "$PYTHON" "$scripts_dir/test-planner-workflow.py" || fail=$((fail + 1))
    for focused in \
      "$scripts_dir/../skills/initialize-coherence/scripts/test_contract.py" \
      "$scripts_dir/../skills/planning-brainstorming/scripts/test_contract.py" \
      "$scripts_dir/../skills/task-generation/scripts/test_contract.py" \
      "$scripts_dir/../skills/coordinate-implementation/scripts/test_batching_contract.py" \
      "$scripts_dir/../skills/coordinate-implementation/scripts/test_intake_contract.py" \
      "$scripts_dir/../skills/coordinate-implementation/scripts/test_state_contract.py" \
      "$scripts_dir/test-task-commit-contract.py"; do
      "$PYTHON" "$focused" || fail=$((fail + 1))
    done
    if "$PYTHON" -c 'import jsonschema, langgraph, yaml' >/dev/null 2>&1; then
      "$PYTHON" "$scripts_dir/../skills/task-generation/scripts/test_check_task_order.py" || fail=$((fail + 1))
    else
      "$PYTHON" "$scripts_dir/../skills/task-generation/scripts/test_check_task_order.py" TaskOrderTests || fail=$((fail + 1))
      echo "Structured runtime adapter checks: NOT VERIFIED (optional runtime dependencies unavailable; select ready COHERENCE_PYTHON). Not production acceptance."
    fi
    "$PYTHON" "$scripts_dir/check-planner-workflow.py" --active-consumers || fail=$((fail + 1))
  else
    echo "SKIP planner workflow checks (custom skills directory; suite-wide artifacts unavailable)"
  fi
fi
[ "$fail" -eq 0 ]