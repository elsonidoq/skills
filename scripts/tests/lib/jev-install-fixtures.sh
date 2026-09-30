#!/bin/sh
# Deterministic fixture helpers for Jev-on installer tests. They only create
# temporary fake commands; no helper can reach a real Jev executable.

jev_fixture_setup() {
	if [ -n "${JEV_FIXTURE_ROOT:-}" ]; then
		printf '%s\n' "jev fixture is already active" >&2
		return 2
	fi

	JEV_FIXTURE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/jev-install-fixture.XXXXXX")" || return 1
	JEV_FIXTURE_HOME="$JEV_FIXTURE_ROOT/home"
	JEV_FIXTURE_BIN="$JEV_FIXTURE_ROOT/bin"
	JEV_FIXTURE_STAGED="$JEV_FIXTURE_ROOT/staged"
	JEV_FIXTURE_ROLLBACK="$JEV_FIXTURE_ROOT/rollback"
	JEV_FIXTURE_LOG="$JEV_FIXTURE_ROOT/fake-commands.log"

	if [ "${HOME+x}" = x ]; then
		JEV_FIXTURE_HAD_HOME=1
		JEV_FIXTURE_PREVIOUS_HOME=$HOME
	else
		JEV_FIXTURE_HAD_HOME=0
		JEV_FIXTURE_PREVIOUS_HOME=
	fi
	if [ "${PATH+x}" = x ]; then
		JEV_FIXTURE_HAD_PATH=1
		JEV_FIXTURE_PREVIOUS_PATH=$PATH
	else
		JEV_FIXTURE_HAD_PATH=0
		JEV_FIXTURE_PREVIOUS_PATH=
	fi
	if [ "${XDG_STATE_HOME+x}" = x ]; then
		JEV_FIXTURE_HAD_XDG_STATE_HOME=1
		JEV_FIXTURE_PREVIOUS_XDG_STATE_HOME=$XDG_STATE_HOME
	else
		JEV_FIXTURE_HAD_XDG_STATE_HOME=0
		JEV_FIXTURE_PREVIOUS_XDG_STATE_HOME=
	fi

	mkdir -p "$JEV_FIXTURE_HOME" "$JEV_FIXTURE_BIN" "$JEV_FIXTURE_STAGED" "$JEV_FIXTURE_ROLLBACK" || {
		rm -rf "$JEV_FIXTURE_ROOT"
		return 1
	}
	: > "$JEV_FIXTURE_LOG" || return 1

	cat > "$JEV_FIXTURE_BIN/pi" <<'EOF'
#!/bin/sh
case "${1:-}" in
	--version) printf '%s\n' "${FAKE_PI_VERSION:-0.87.1}" ;;
	list) printf '%s\n' "${FAKE_PI_LIST:-}" ;;
	install) printf '%s\n' "pi-install" >> "$JEV_FIXTURE_LOG"; exit "${FAKE_PI_INSTALL_EXIT:-0}" ;;
	*) printf '%s\n' "pi" >> "$JEV_FIXTURE_LOG"; exit "${FAKE_PI_EXIT:-0}" ;;
esac
EOF
	cat > "$JEV_FIXTURE_BIN/node" <<'EOF'
#!/bin/sh
case "${1:-}" in
	--version|-v) printf '%s\n' "${FAKE_NODE_VERSION:-v22.23.3}" ;;
	*) printf '%s\n' "node" >> "$JEV_FIXTURE_LOG"; printf '%s\n' "${FAKE_NODE_STDOUT:-}"; exit "${FAKE_NODE_EXIT:-0}" ;;
esac
EOF
	cat > "$JEV_FIXTURE_BIN/jev" <<'EOF'
#!/bin/sh
case "${1:-}" in
	--version) printf '%s\n' "${FAKE_JEV_VERSION:-jev-cli 0.6.3}" ;;
	auth)
		if [ "${2:-}" = test ]; then
			printf '%s\n' "jev-auth-test" >> "$JEV_FIXTURE_LOG"
			printf '%s\n' "${FAKE_JEV_AUTH_OUTPUT:-authenticated}"
			exit "${FAKE_JEV_AUTH_EXIT:-0}"
		fi
		printf '%s\n' "jev-auth" >> "$JEV_FIXTURE_LOG"
		exit "${FAKE_JEV_EXIT:-0}"
		;;
	run) printf '%s\n' "jev-run" >> "$JEV_FIXTURE_LOG"; printf '%s\n' "${FAKE_JEV_RUN_OUTPUT:-}"; exit "${FAKE_JEV_RUN_EXIT:-0}" ;;
	*) printf '%s\n' "jev" >> "$JEV_FIXTURE_LOG"; exit "${FAKE_JEV_EXIT:-0}" ;;
esac
EOF
	cat > "$JEV_FIXTURE_BIN/specify" <<'EOF'
#!/bin/sh
case "${1:-}" in
	--version) printf '%s\n' "${FAKE_SPECIFY_VERSION:-1.0.12}" ;;
	preset) printf '%s\n' "specify-preset" >> "$JEV_FIXTURE_LOG"; printf '%s\n' "${FAKE_SPECIFY_PRESET_OUTPUT:-}"; exit "${FAKE_SPECIFY_PRESET_EXIT:-0}" ;;
	artifact) printf '%s\n' "specify-artifact" >> "$JEV_FIXTURE_LOG"; printf '%s\n' "${FAKE_SPECIFY_ARTIFACT_OUTPUT:-}"; exit "${FAKE_SPECIFY_ARTIFACT_EXIT:-0}" ;;
	*) printf '%s\n' "specify" >> "$JEV_FIXTURE_LOG"; exit "${FAKE_SPECIFY_EXIT:-0}" ;;
esac
EOF
	chmod 700 "$JEV_FIXTURE_BIN/pi" "$JEV_FIXTURE_BIN/node" "$JEV_FIXTURE_BIN/jev" "$JEV_FIXTURE_BIN/specify" || return 1

	HOME=$JEV_FIXTURE_HOME
	PATH=$JEV_FIXTURE_BIN:$JEV_FIXTURE_PREVIOUS_PATH
	XDG_STATE_HOME=$JEV_FIXTURE_ROOT/state
	export HOME PATH XDG_STATE_HOME JEV_FIXTURE_ROOT JEV_FIXTURE_HOME JEV_FIXTURE_BIN
	export JEV_FIXTURE_STAGED JEV_FIXTURE_ROLLBACK JEV_FIXTURE_LOG
	export FAKE_PI_VERSION FAKE_PI_LIST FAKE_PI_INSTALL_EXIT FAKE_PI_EXIT
	export FAKE_NODE_VERSION FAKE_NODE_STDOUT FAKE_NODE_EXIT
	export FAKE_JEV_VERSION FAKE_JEV_AUTH_OUTPUT FAKE_JEV_AUTH_EXIT FAKE_JEV_RUN_OUTPUT FAKE_JEV_RUN_EXIT FAKE_JEV_EXIT
	export FAKE_SPECIFY_VERSION FAKE_SPECIFY_PRESET_OUTPUT FAKE_SPECIFY_PRESET_EXIT
	export FAKE_SPECIFY_ARTIFACT_OUTPUT FAKE_SPECIFY_ARTIFACT_EXIT FAKE_SPECIFY_EXIT
}

jev_fixture_cleanup() {
	[ -n "${JEV_FIXTURE_ROOT:-}" ] || return 0
	rm -rf "$JEV_FIXTURE_ROOT"

	if [ "$JEV_FIXTURE_HAD_HOME" = 1 ]; then HOME=$JEV_FIXTURE_PREVIOUS_HOME; export HOME; else unset HOME; fi
	if [ "$JEV_FIXTURE_HAD_PATH" = 1 ]; then PATH=$JEV_FIXTURE_PREVIOUS_PATH; export PATH; else unset PATH; fi
	if [ "$JEV_FIXTURE_HAD_XDG_STATE_HOME" = 1 ]; then
		XDG_STATE_HOME=$JEV_FIXTURE_PREVIOUS_XDG_STATE_HOME
		export XDG_STATE_HOME
	else
		unset XDG_STATE_HOME
	fi

	unset JEV_FIXTURE_ROOT JEV_FIXTURE_HOME JEV_FIXTURE_BIN JEV_FIXTURE_STAGED JEV_FIXTURE_ROLLBACK JEV_FIXTURE_LOG
	unset JEV_FIXTURE_HAD_HOME JEV_FIXTURE_PREVIOUS_HOME JEV_FIXTURE_HAD_PATH JEV_FIXTURE_PREVIOUS_PATH
	unset JEV_FIXTURE_HAD_XDG_STATE_HOME JEV_FIXTURE_PREVIOUS_XDG_STATE_HOME
}

# Configure the fake, never-real `jev auth test` outcome for the next test.
jev_fixture_set_jev_auth_result() {
	FAKE_JEV_AUTH_EXIT=${1:-0}
	FAKE_JEV_AUTH_OUTPUT=${2:-authenticated}
	export FAKE_JEV_AUTH_EXIT FAKE_JEV_AUTH_OUTPUT
}

# Write a staged resource below the fixture root. Absolute and traversing names are rejected.
jev_fixture_stage_resource() {
	case "${1:-}" in
		""|/*|..|../*|*/../*|*/..) printf '%s\n' "invalid staged resource name" >&2; return 2 ;;
	esac
	[ -n "${JEV_FIXTURE_STAGED:-}" ] || return 2
	resource=$JEV_FIXTURE_STAGED/$1
	mkdir -p "$(dirname "$resource")" || return 1
	printf '%s' "${2:-}" > "$resource"
}

jev_fixture_staged_path() {
	case "${1:-}" in
		""|/*|..|../*|*/../*|*/..) return 2 ;;
	esac
	[ -n "${JEV_FIXTURE_STAGED:-}" ] || return 2
	printf '%s\n' "$JEV_FIXTURE_STAGED/$1"
}

jev_fixture_assert_owned_path() {
	case "${1:-}" in
		"$JEV_FIXTURE_ROOT"/*) return 0 ;;
		*) printf '%s\n' "rollback path must be inside fixture root" >&2; return 2 ;;
	esac
}

# Save and restore only fixture-owned resources, including an explicit absent state.
jev_fixture_capture_rollback() {
	target=${1:-}
	jev_fixture_assert_owned_path "$target" || return $?
	relative=${target#"$JEV_FIXTURE_ROOT"/}
	backup=$JEV_FIXTURE_ROLLBACK/$relative
	mkdir -p "$(dirname "$backup")" || return 1
	rm -rf "$backup" "$backup.absent"
	if [ -e "$target" ] || [ -L "$target" ]; then
		cp -R "$target" "$backup" || return 1
	else
		: > "$backup.absent" || return 1
	fi
}

jev_fixture_restore_rollback() {
	target=${1:-}
	jev_fixture_assert_owned_path "$target" || return $?
	relative=${target#"$JEV_FIXTURE_ROOT"/}
	backup=$JEV_FIXTURE_ROLLBACK/$relative
	if [ -e "$backup" ] || [ -L "$backup" ]; then
		rm -rf "$target"
		mkdir -p "$(dirname "$target")" || return 1
		cp -R "$backup" "$target" || return 1
		return 0
	fi
	if [ -e "$backup.absent" ]; then
		rm -rf "$target"
		return 0
	fi
	printf '%s\n' "no rollback state for fixture resource" >&2
	return 2
}

jev_fixture_self_check() {
	old_path=$PATH
	jev_fixture_setup || return 1
	root=$JEV_FIXTURE_ROOT
	for command_name in pi node jev specify; do
		resolved=$(command -v "$command_name") || {
			jev_fixture_cleanup
			return 1
		}
		[ "$resolved" = "$JEV_FIXTURE_BIN/$command_name" ] || {
			jev_fixture_cleanup
			return 1
		}
	done
	jev --version >/dev/null || {
		jev_fixture_cleanup
		return 1
	}
	jev auth test >/dev/null || {
		jev_fixture_cleanup
		return 1
	}
	grep -Fx "jev-auth-test" "$JEV_FIXTURE_LOG" >/dev/null || {
		jev_fixture_cleanup
		return 1
	}
	jev_fixture_cleanup || return 1
	[ "$PATH" = "$old_path" ] && [ ! -e "$root" ] || return 1
	printf '%s\n' "jev-install-fixtures self-check: ok"
}

case "$0" in
	*jev-install-fixtures.sh) jev_fixture_self_check || exit 1 ;;
esac
