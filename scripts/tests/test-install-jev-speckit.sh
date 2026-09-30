#!/usr/bin/env bash
# Deterministic acceptance fixture for the project-local SpecKit Jev preset.
# It never invokes Jev and uses disposable projects only.
set -u

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
INSTALLER="$ROOT_DIR/scripts/install-jev-speckit.sh"
PRESET_SOURCE="$ROOT_DIR/configs/speckit/presets/jev-seams"
COMMANDS=(speckit.analyze speckit.checklist speckit.clarify speckit.tasks)
PASS=0
FAIL=0

fail() {
	printf '%s\n' "$*" >&2
	return 1
}

new_project() {
	PROJECT="$(mktemp -d "${TMPDIR:-/tmp}/jev-speckit-project.XXXXXX")" || return 1
	cp -R "$ROOT_DIR/.specify" "$PROJECT/.specify" || return 1
	mkdir -p "$PROJECT/.pi/prompts" || return 1
	for command_id in "${COMMANDS[@]}"; do
		printf '%s\n' "core-prompt-before-$command_id" > "$PROJECT/.pi/prompts/$command_id.md" || return 1
	done
	PROMPT_SNAPSHOT="$PROJECT/prompt-snapshot"
	cp -R "$PROJECT/.pi/prompts" "$PROMPT_SNAPSHOT" || return 1
	PI_CODING_AGENT_DIR="$PROJECT/pi-agent"
	mkdir -p "$PI_CODING_AGENT_DIR/extensions" || return 1
	ln -s "$ROOT_DIR/extensions/jev-metrics" "$PI_CODING_AGENT_DIR/extensions/jev-metrics" || return 1
	export PI_CODING_AGENT_DIR
}

cleanup_project() {
	[ -z "${PROJECT:-}" ] || rm -rf "$PROJECT"
	PROJECT=
}

run_installer() {
	INSTALL_OUTPUT="$(cd "$PROJECT" && "$INSTALLER" --project "$PROJECT" "$@" 2>&1)"
	INSTALL_STATUS=$?
}

assert_no_preset() {
	[ ! -e "$PROJECT/.specify/presets/jev-seams" ] || return 1
	if [ -e "$PROJECT/.specify/presets/.registry" ]; then
		[ "$(grep -Fc 'jev-seams' "$PROJECT/.specify/presets/.registry" || :)" -eq 0 ] || return 1
	fi
}

assert_core_prompts_restored() {
	diff -ru "$PROMPT_SNAPSHOT" "$PROJECT/.pi/prompts"
}

assert_exact_composition() {
	local command_id resolve_output artifact_json
	for command_id in "${COMMANDS[@]}"; do
		resolve_output="$(cd "$PROJECT" && specify preset resolve "$command_id" 2>&1)" || return 1
		case "$resolve_output" in *"jev-seams"*) : ;; *) fail "missing Jev preset in resolver output for $command_id" || return 1 ;; esac
		case "$resolve_output" in *"[append]"*) : ;; *) fail "missing append strategy in resolver output for $command_id" || return 1 ;; esac
		case "$resolve_output" in *"[base]"*"core"*) : ;; *) fail "missing core base in resolver output for $command_id" || return 1 ;; esac
		artifact_json="$(cd "$PROJECT" && specify artifact info "$command_id" --json)" || return 1
		ARTIFACT_JSON="$artifact_json" python3 - "$command_id" <<'PY'
import json
import os
import sys

command_id = sys.argv[1]
payload = json.loads(os.environ["ARTIFACT_JSON"])
stack = payload.get("stack")
if not isinstance(stack, list):
    raise SystemExit(f"{command_id}: artifact stack missing")
append_layers = [row for row in stack if row.get("presetId") == "jev-seams" and row.get("strategy") == "append"]
core_layers = [row for row in stack if row.get("layer") is None and row.get("strategy") == "replace"]
if len(append_layers) != 1 or len(core_layers) != 1:
    raise SystemExit(f"{command_id}: expected exactly one append layer and one core layer")
manifest_path = append_layers[0].get("manifestPath")
if manifest_path != ".specify/presets/jev-seams/preset.yml":
    raise SystemExit(f"{command_id}: append layer is not registered from the project preset")
PY
	done
}

assert_preset_source_owns_no_generated_prompts() {
	[ ! -d "$PRESET_SOURCE/.pi/prompts" ] || return 1
	! grep -R -F '.pi/prompts/' "$PRESET_SOURCE" >/dev/null 2>&1
}

assert_generated_prompts_contain_core_and_append() {
	local command_id core_marker prompt
	for command_id in "${COMMANDS[@]}"; do
		case "$command_id" in
			speckit.analyze) core_marker="Perform a non-destructive cross-artifact consistency" ;;
			speckit.checklist) core_marker="Generate a custom checklist for the current feature" ;;
			speckit.clarify) core_marker="Identify underspecified areas in the current feature spec" ;;
			speckit.tasks) core_marker="Generate an actionable, dependency-ordered tasks.md" ;;
		esac
		prompt="$PROJECT/.pi/prompts/$command_id.md"
		grep -F "$core_marker" "$prompt" >/dev/null || return 1
		grep -F "Optional Jev-on advisory" "$prompt" >/dev/null || return 1
	done
}

case_installs_all_or_none_and_reports_composition() (
	new_project || exit 1
	trap cleanup_project EXIT
	run_installer
	[ "$INSTALL_STATUS" -eq 0 ] || { printf '%s\n' "$INSTALL_OUTPUT" >&2; exit 1; }
	[ -d "$PROJECT/.specify/presets/jev-seams" ] || exit 1
	assert_preset_source_owns_no_generated_prompts || exit 1
	assert_exact_composition || exit 1
	assert_generated_prompts_contain_core_and_append || exit 1
)

case_missing_tracker_keeps_all_disabled() (
	new_project || exit 1
	trap cleanup_project EXIT
	rm -f "$PI_CODING_AGENT_DIR/extensions/jev-metrics"
	run_installer
	[ "$INSTALL_STATUS" -ne 0 ] || exit 1
	assert_no_preset || exit 1
	assert_core_prompts_restored || exit 1
	case "$INSTALL_OUTPUT" in
		*"SpecKit preflight failed: active tracker"*"Observed:"*"Resolution:"*"No SpecKit Jev seam was enabled."*) : ;;
		*) printf '%s\n' "$INSTALL_OUTPUT" >&2; exit 1 ;;
	esac
)

# T030 must honor these deterministic fault-injection flags before changing any
# active path. They make all-or-none and rollback behavior observable without Jev.
case_subset_activation_is_rejected() (
	new_project || exit 1
	trap cleanup_project EXIT
	JEV_SPECKIT_TEST_SUBSET=1
	export JEV_SPECKIT_TEST_SUBSET
	run_installer
	unset JEV_SPECKIT_TEST_SUBSET
	[ "$INSTALL_STATUS" -ne 0 ] || exit 1
	assert_no_preset || exit 1
	assert_core_prompts_restored || exit 1
)

case_incompatible_resolver_keeps_all_disabled() (
	new_project || exit 1
	trap cleanup_project EXIT
	shim_dir="$PROJECT/shim-bin"
	mkdir -p "$shim_dir" || exit 1
	cat > "$shim_dir/specify" <<EOF
#!/bin/sh
if [ "\${1:-}" = "--version" ]; then
	printf '%s\\n' '0.9.0'
	exit 0
fi
exec "$(command -v specify)" "\$@"
EOF
	chmod 700 "$shim_dir/specify" || exit 1
	INSTALL_OUTPUT="$(cd "$PROJECT" && PATH="$shim_dir:$PATH" "$INSTALLER" --project "$PROJECT" 2>&1)"
	INSTALL_STATUS=$?
	[ "$INSTALL_STATUS" -ne 0 ] || exit 1
	assert_no_preset || exit 1
)

case_rollback_restores_core_prompts() (
	new_project || exit 1
	trap cleanup_project EXIT
	JEV_SPECKIT_FAIL_AFTER_PRESET=1
	export JEV_SPECKIT_FAIL_AFTER_PRESET
	run_installer
	unset JEV_SPECKIT_FAIL_AFTER_PRESET
	[ "$INSTALL_STATUS" -ne 0 ] || exit 1
	assert_no_preset || exit 1
	assert_core_prompts_restored || exit 1
)

case_uninstall_reconciles_original_core_prompts() (
	new_project || exit 1
	trap cleanup_project EXIT
	run_installer
	[ "$INSTALL_STATUS" -eq 0 ] || exit 1
	run_installer --uninstall
	[ "$INSTALL_STATUS" -eq 0 ] || { printf '%s\n' "$INSTALL_OUTPUT" >&2; exit 1; }
	assert_no_preset || exit 1
	assert_core_prompts_restored || exit 1
)

run_case() {
	local name=$1
	shift
	if "$@"; then
		PASS=$((PASS + 1))
		printf '%s\n' "ok - $name"
	else
		FAIL=$((FAIL + 1))
		printf '%s\n' "not ok - $name"
	fi
}

if [ ! -x "$INSTALLER" ]; then
	printf '%s\n' "not ok - project-local SpecKit installer is unavailable: $INSTALLER"
	printf '%s\n' "----"
	printf '%s\n' "0 passed, 1 failed"
	exit 1
fi

run_case "installs all four append layers with resolver and artifact evidence" case_installs_all_or_none_and_reports_composition
run_case "missing active tracker keeps all four SpecKit seams disabled" case_missing_tracker_keeps_all_disabled
run_case "rejects a requested subset before changing generated prompts" case_subset_activation_is_rejected
run_case "incompatible SpecKit resolver leaves all four seams disabled" case_incompatible_resolver_keeps_all_disabled
run_case "injected activation failure rolls back the preset and core prompts" case_rollback_restores_core_prompts
run_case "uninstall reconciles original core prompts" case_uninstall_reconciles_original_core_prompts

printf '%s\n' "----"
printf '%s\n' "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
