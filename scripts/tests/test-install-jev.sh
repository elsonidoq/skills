#!/usr/bin/env bash
# Deterministic manual/Jev-on installer acceptance tests. All commands resolve
# inside the fixture PATH; this script must never invoke a real Jev executable.
set -u

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
INSTALLER="$ROOT_DIR/scripts/install.sh"
# shellcheck source=lib/jev-install-fixtures.sh
. "$ROOT_DIR/scripts/tests/lib/jev-install-fixtures.sh"

PASS=0
FAIL=0

assert_contains() {
	case "$1" in
		*"$2"*) return 0 ;;
		*) printf '%s\n' "missing output: $2" >&2; return 1 ;;
	esac
}

assert_not_contains() {
	case "$1" in
		*"$2"*) printf '%s\n' "unexpected output: $2" >&2; return 1 ;;
		*) return 0 ;;
	esac
}

fixture_begin() {
	jev_fixture_setup || return 1
	PI_CODING_AGENT_DIR="$JEV_FIXTURE_HOME/.pi/agent"
	FAKE_PI_LIST='npm:pi-subagents@0.73.1
npm:pi-ask-user@0.15.1'
	export PI_CODING_AGENT_DIR FAKE_PI_LIST
}

run_installer() {
	INSTALL_OUTPUT="$($INSTALLER "$@" 2>&1)"
	INSTALL_STATUS=$?
}

assert_no_activation() {
	[ ! -e "$PI_CODING_AGENT_DIR/extensions/jev-metrics" ] &&
		[ ! -L "$PI_CODING_AGENT_DIR/extensions/jev-metrics" ] &&
		[ ! -e "$PI_CODING_AGENT_DIR/jev-metrics/global-seams-enabled" ]
}

assert_failure_diagnostic() {
	label=$1
	observed=$2
	action=$3
	[ "$INSTALL_STATUS" -ne 0 ] || { printf '%s\n' "installer unexpectedly succeeded" >&2; return 1; }
	assert_contains "$INSTALL_OUTPUT" "Jev-on preflight failed: $label" &&
		assert_contains "$INSTALL_OUTPUT" "Observed: $observed" &&
		assert_contains "$INSTALL_OUTPUT" "Resolution: $action" &&
		assert_contains "$INSTALL_OUTPUT" "No optimized seam was enabled." &&
		assert_no_activation
}

case_manual_default() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	rm -f "$JEV_FIXTURE_BIN/jev"
	run_installer
	[ "$INSTALL_STATUS" -eq 0 ] || { printf '%s\n' "$INSTALL_OUTPUT" >&2; exit 1; }
	assert_no_activation || exit 1
	for skill_id in scientific-method-debugging receiving-code-review coordinate-implementation track-open-issue; do
		link="$JEV_FIXTURE_HOME/.agents/skills/$skill_id"
		[ -L "$link" ] || { printf '%s\n' "manual skill missing: $skill_id" >&2; exit 1; }
	done
	assert_not_contains "$(cat "$JEV_FIXTURE_LOG")" "jev-auth-test" || exit 1
)

case_incompatible_pi() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	FAKE_PI_VERSION=0.88.0; export FAKE_PI_VERSION
	run_installer --jev-on
	assert_failure_diagnostic "Pi compatibility" "pi 0.88.0" "install Pi 0.87.x (tested 0.87.1)" || exit 1
	assert_not_contains "$(cat "$JEV_FIXTURE_LOG")" "jev-auth-test" || exit 1
)

case_incompatible_node() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	FAKE_NODE_VERSION=v20.19.0; export FAKE_NODE_VERSION
	run_installer --jev-on
	assert_failure_diagnostic "Node runtime" "node v20.19.0" "install Node.js 22 or a proven compatible later runtime" || exit 1
	assert_not_contains "$(cat "$JEV_FIXTURE_LOG")" "jev-auth-test" || exit 1
)

case_tracker_load_failure() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	FAKE_TRACKER_LOAD_EXIT=1; export FAKE_TRACKER_LOAD_EXIT
	run_installer --jev-on
	assert_failure_diagnostic "tracker load/registration" "load harness exit 1" "repair the jev-metrics extension and rerun deterministic extension tests" || exit 1
	assert_not_contains "$(cat "$JEV_FIXTURE_LOG")" "jev-auth-test" || exit 1
)

case_incompatible_jev() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	FAKE_JEV_VERSION='jev-cli 0.7.0'; export FAKE_JEV_VERSION
	run_installer --jev-on
	assert_failure_diagnostic "Jev CLI compatibility" "jev-cli 0.7.0" "install jev-cli 0.6.3" || exit 1
	assert_not_contains "$(cat "$JEV_FIXTURE_LOG")" "jev-auth-test" || exit 1
)

case_auth_failure() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	jev_fixture_set_jev_auth_result 1 'credential-secret-SHOULD-NOT-LEAK'
	run_installer --jev-on
	assert_failure_diagnostic "Jev authentication" "jev auth test exit 1" "configure the Jev provider credentials and rerun jev auth test" || exit 1
	assert_not_contains "$INSTALL_OUTPUT" "credential-secret-SHOULD-NOT-LEAK" || exit 1
	[ "$(grep -Fxc 'jev-auth-test' "$JEV_FIXTURE_LOG")" -eq 1 ] || exit 1
)

case_deterministic_failure() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	FAKE_NODE_TEST_EXIT=1
	FAKE_NODE_TEST_OUTPUT='test detail SHOULD-NOT-BE-REPORTED'
	export FAKE_NODE_TEST_EXIT FAKE_NODE_TEST_OUTPUT
	run_installer --jev-on
	assert_failure_diagnostic "deterministic checks" "extension test exit 1" "fix the deterministic extension tests before enabling Jev-on" || exit 1
	assert_not_contains "$INSTALL_OUTPUT" "test detail SHOULD-NOT-BE-REPORTED" || exit 1
	assert_no_activation || exit 1
)

case_success_order() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	run_installer --jev-on
	[ "$INSTALL_STATUS" -eq 0 ] || { printf '%s\n' "$INSTALL_OUTPUT" >&2; exit 1; }
	tracker="$PI_CODING_AGENT_DIR/extensions/jev-metrics"
	marker="$PI_CODING_AGENT_DIR/jev-metrics/global-seams-enabled"
	[ -L "$tracker" ] || { printf '%s\n' "tracker was not activated" >&2; exit 1; }
	[ "$(readlink -f "$tracker")" = "$(readlink -f "$ROOT_DIR/extensions/jev-metrics")" ] || exit 1
	[ -f "$marker" ] || { printf '%s\n' "global seam marker missing" >&2; exit 1; }
	expected='scientific-method-debugging
receiving-code-review
coordinate-implementation
track-open-issue'
	[ "$(cat "$marker")" = "$expected" ] || { printf '%s\n' "global seam set is not exact" >&2; exit 1; }
	tracker_line=$(printf '%s\n' "$INSTALL_OUTPUT" | grep -nF 'activated tracker:' | cut -d: -f1)
	seam_line=$(printf '%s\n' "$INSTALL_OUTPUT" | grep -nF 'activated global seams:' | cut -d: -f1)
	[ -n "$tracker_line" ] && [ -n "$seam_line" ] && [ "$tracker_line" -lt "$seam_line" ] || {
		printf '%s\n' "tracker was not activated before seams" >&2; exit 1;
	}
	assert_contains "$INSTALL_OUTPUT" 'run `/reload`' || exit 1
	[ "$(grep -Fxc 'jev-auth-test' "$JEV_FIXTURE_LOG")" -eq 1 ] || exit 1
	grep -Fx 'tracker-load-check' "$JEV_FIXTURE_LOG" >/dev/null || exit 1
	grep -Fx 'tracker-active-check' "$JEV_FIXTURE_LOG" >/dev/null || exit 1
	grep -Fx 'node-test' "$JEV_FIXTURE_LOG" >/dev/null || exit 1
)

case_activation_rollback() (
	fixture_begin || exit 1
	trap jev_fixture_cleanup EXIT
	tracker="$PI_CODING_AGENT_DIR/extensions/jev-metrics"
	mkdir -p "$tracker"
	printf '%s\n' 'pre-install tracker state' > "$tracker/original"
	JEV_INSTALL_FAIL_AFTER_TRACKER=1; export JEV_INSTALL_FAIL_AFTER_TRACKER
	run_installer --jev-on
	[ "$INSTALL_STATUS" -ne 0 ] || exit 1
	[ -f "$tracker/original" ] || { printf '%s\n' "pre-install tracker was not restored" >&2; exit 1; }
	[ "$(cat "$tracker/original")" = 'pre-install tracker state' ] || exit 1
	[ ! -e "$PI_CODING_AGENT_DIR/jev-metrics/global-seams-enabled" ] || exit 1
	assert_contains "$INSTALL_OUTPUT" "Jev-on activation failed: injected failure after tracker activation" || exit 1
	assert_contains "$INSTALL_OUTPUT" "Observed: injected failure after tracker activation" || exit 1
	assert_contains "$INSTALL_OUTPUT" "Resolution: resolve the active-path conflict or permission failure, then rerun --jev-on" || exit 1
	assert_contains "$INSTALL_OUTPUT" "Rollback: restored pre-activation tracker and seam state." || exit 1
	assert_contains "$INSTALL_OUTPUT" "No optimized seam was enabled." || exit 1
	assert_not_contains "$INSTALL_OUTPUT" "activated global seams:" || exit 1
)

run_case() {
	name=$1
	shift
	if "$@"; then
		PASS=$((PASS + 1))
		printf '%s\n' "ok - $name"
	else
		FAIL=$((FAIL + 1))
		printf '%s\n' "not ok - $name"
	fi
}

run_case "manual default needs neither Jev nor tracker" case_manual_default
run_case "Jev-on rejects incompatible Pi before activation" case_incompatible_pi
run_case "Jev-on rejects incompatible Node before activation" case_incompatible_node
run_case "Jev-on rejects tracker load/registration failure before activation" case_tracker_load_failure
run_case "Jev-on rejects incompatible Jev CLI before activation" case_incompatible_jev
run_case "Jev-on redacts failed auth output before activation" case_auth_failure
run_case "Jev-on rejects deterministic check failure before activation" case_deterministic_failure
run_case "Jev-on activates tracker before the exact four seams" case_success_order
run_case "Jev-on activation failure restores pre-install state" case_activation_rollback

printf '%s\n' "----"
printf '%s\n' "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
