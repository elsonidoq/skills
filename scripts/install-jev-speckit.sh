#!/usr/bin/env bash
# Transactionally install or remove the project-local Jev append preset using
# SpecKit's supported preset registry and reconciliation commands.
set -uo pipefail

SUITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PRESET_SOURCE="$SUITE_DIR/configs/speckit/presets/jev-seams"
TRACKER_SOURCE="$SUITE_DIR/extensions/jev-metrics"
PRESET_ID="jev-seams"
REQ_SPECIFY="1.0.12"
COMMANDS=(speckit.analyze speckit.checklist speckit.clarify speckit.tasks)
PROJECT=
UNINSTALL=0

while [ "$#" -gt 0 ]; do
	case "$1" in
		--project)
			shift
			[ "$#" -gt 0 ] || { printf '%s\n' "usage: $0 --project DIR [--uninstall]" >&2; exit 2; }
			PROJECT=$1
			;;
		--uninstall) UNINSTALL=1 ;;
		-h|--help) printf '%s\n' "usage: $0 --project DIR [--uninstall]"; exit 0 ;;
		*) printf '%s\n' "usage: $0 --project DIR [--uninstall]" >&2; exit 2 ;;
	esac
	shift
done
[ -n "$PROJECT" ] || { printf '%s\n' "ERROR: --project DIR is required" >&2; exit 2; }

info() { printf '==> %s\n' "$*"; }
preflight_failure() {
	printf '%s\n' "ERROR: SpecKit preflight failed: $1" >&2
	printf '%s\n' "Observed: $2" >&2
	printf '%s\n' "Resolution: $3" >&2
	printf '%s\n' "No SpecKit Jev seam was enabled." >&2
	exit 1
}

if [ ! -d "$PROJECT" ]; then
	preflight_failure "target project" "project directory not found: $PROJECT" "provide an existing SpecKit project with --project"
fi
PROJECT="$(cd "$PROJECT" && pwd -P)"
SPECIFY_DIR="$PROJECT/.specify"
PRESETS_DIR="$SPECIFY_DIR/presets"
ACTIVE_PRESET="$PRESETS_DIR/$PRESET_ID"
PROMPTS_DIR="$PROJECT/.pi/prompts"
TRACKER_ACTIVE="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/extensions/jev-metrics"
STAGE_DIR=
ACTIVE_ROLLBACK=
ACTIVATION_STARTED=0
INSTALL_COMPLETE=0

preset_registered_at() {
	local root=$1
	REGISTRY="$root/.specify/presets/.registry" PRESET_ID="$PRESET_ID" python3 - <<'PY' >/dev/null 2>&1
import json
import os
from pathlib import Path
path = Path(os.environ["REGISTRY"])
if not path.is_file():
    raise SystemExit(1)
data = json.loads(path.read_text(encoding="utf-8"))
raise SystemExit(0 if os.environ["PRESET_ID"] in data.get("presets", {}) else 1)
PY
}

snapshot_path() {
	local source=$1 destination=$2
	rm -rf "$destination" "$destination.absent"
	if [ -e "$source" ] || [ -L "$source" ]; then
		cp -a "$source" "$destination"
	else
		: > "$destination.absent"
	fi
}

restore_path() {
	local target=$1 snapshot=$2
	rm -rf "$target"
	if [ -e "$snapshot" ] || [ -L "$snapshot" ]; then
		mkdir -p "$(dirname "$target")"
		cp -a "$snapshot" "$target"
	elif [ ! -e "$snapshot.absent" ]; then
		return 1
	fi
}

capture_active_state() {
	ACTIVE_ROLLBACK="$STAGE_DIR/active-rollback"
	mkdir -p "$ACTIVE_ROLLBACK" || return 1
	# Generated .pi/prompts are deliberately not copied. SpecKit owns their
	# reconciliation; only the preset registry is snapshotted transactionally.
	snapshot_path "$PRESETS_DIR" "$ACTIVE_ROLLBACK/presets" || return 1
}

reconcile_without_jev() {
	local target=$1
	if [ -d "$target/.specify/presets/$PRESET_ID" ] || preset_registered_at "$target"; then
		(cd "$target" && specify preset remove "$PRESET_ID" >/dev/null 2>&1) || return 1
	else
		# Restoring a registry snapshot that predates the preset does not itself
		# regenerate integration artifacts. Add/remove through SpecKit to force a
		# supported reconciliation from the remaining layers.
		(cd "$target" && specify preset add --dev "$PRESET_SOURCE" >/dev/null 2>&1) || return 1
		(cd "$target" && specify preset remove "$PRESET_ID" >/dev/null 2>&1) || return 1
	fi
}

restore_active_state() {
	local rollback_ok=1
	restore_path "$PRESETS_DIR" "$ACTIVE_ROLLBACK/presets" || rollback_ok=0
	reconcile_without_jev "$PROJECT" || rollback_ok=0
	verify_core_composition "$PROJECT" "$STAGE_DIR/rollback-evidence" || rollback_ok=0
	ACTIVATION_STARTED=0
	if [ "$rollback_ok" -eq 1 ]; then
		printf '%s\n' "Rollback: restored the preset registry and reconciled all four commands from remaining layers." >&2
		return 0
	fi
	printf '%s\n' "Rollback: incomplete; inspect $PRESETS_DIR and SpecKit resolver state before retrying." >&2
	return 1
}

activation_failure() {
	local reason=$1
	printf '%s\n' "ERROR: SpecKit activation failed: $reason" >&2
	printf '%s\n' "Observed: $reason" >&2
	printf '%s\n' "Resolution: correct the resolver, registry, or integration failure and retry the complete four-command install" >&2
	if restore_active_state; then
		printf '%s\n' "No SpecKit Jev seam was enabled." >&2
	else
		printf '%s\n' "SpecKit seam state could not be confirmed; manual recovery is required." >&2
	fi
	exit 1
}

cleanup() {
	if [ "$ACTIVATION_STARTED" -eq 1 ] && [ "$INSTALL_COMPLETE" -ne 1 ]; then
		restore_active_state || :
	fi
	[ -z "$STAGE_DIR" ] || rm -rf "$STAGE_DIR"
}
trap cleanup EXIT

check_source_manifest() {
	PRESET_MANIFEST="$PRESET_SOURCE/preset.yml" python3 - <<'PY'
import os
from pathlib import Path

manifest = Path(os.environ["PRESET_MANIFEST"])
entries = []
current = None
for raw_line in manifest.read_text(encoding="utf-8").splitlines():
    text = raw_line.strip()
    if text.startswith("- type:"):
        current = {"type": text.split(":", 1)[1].strip().strip("\"'")}
        entries.append(current)
    elif current is not None and ":" in text:
        key, value = text.split(":", 1)
        if key in {"name", "file", "strategy"}:
            current[key] = value.strip().strip("\"'")

expected = {
    "speckit.analyze",
    "speckit.checklist",
    "speckit.clarify",
    "speckit.tasks",
}
if len(entries) != 4 or {entry.get("name") for entry in entries} != expected:
    raise SystemExit(1)
for entry in entries:
    if entry.get("type") != "command" or entry.get("strategy") != "append":
        raise SystemExit(1)
    path = manifest.parent / entry.get("file", "")
    if not path.is_file():
        raise SystemExit(1)
PY
}

verify_composition() {
	local target=$1 evidence_dir=$2 command_id resolve_status artifact_status
	mkdir -p "$evidence_dir" || return 1
	for command_id in "${COMMANDS[@]}"; do
		(cd "$target" && specify preset resolve "$command_id") >"$evidence_dir/$command_id.resolve" 2>&1
		resolve_status=$?
		[ "$resolve_status" -eq 0 ] || return 1
		RESOLVE_FILE="$evidence_dir/$command_id.resolve" python3 - <<'PY' || return 1
import os
from pathlib import Path
text = Path(os.environ["RESOLVE_FILE"]).read_text(encoding="utf-8")
if "jev-seams" not in text or "[append]" not in text or "[base]" not in text or "core" not in text:
    raise SystemExit(1)
PY
		(cd "$target" && specify artifact info "$command_id" --json) >"$evidence_dir/$command_id.json" 2>"$evidence_dir/$command_id.artifact-error"
		artifact_status=$?
		[ "$artifact_status" -eq 0 ] || return 1
		ARTIFACT_FILE="$evidence_dir/$command_id.json" COMMAND_ID="$command_id" TARGET="$target" SOURCE="$PRESET_SOURCE" python3 - <<'PY' || return 1
import json
import os
from pathlib import Path

command_id = os.environ["COMMAND_ID"]
target = Path(os.environ["TARGET"])
source = Path(os.environ["SOURCE"])
payload = json.loads(Path(os.environ["ARTIFACT_FILE"]).read_text(encoding="utf-8"))
stack = payload.get("stack")
if not isinstance(stack, list):
    raise SystemExit(1)
append_layers = [
    row for row in stack
    if row.get("presetId") == "jev-seams"
    and row.get("strategy") == "append"
    and row.get("manifestPath") == ".specify/presets/jev-seams/preset.yml"
]
core_layers = [row for row in stack if row.get("layer") is None and row.get("strategy") == "replace"]
if len(append_layers) != 1 or len(core_layers) != 1 or len(stack) != 2:
    raise SystemExit(1)
fragment = (source / "commands" / f"{command_id}.md").read_text(encoding="utf-8").strip()
prompt = (target / ".pi" / "prompts" / f"{command_id}.md").read_text(encoding="utf-8")
if not prompt.startswith("---\n") or prompt.count(fragment) != 1:
    raise SystemExit(1)
prefix = prompt.split(fragment, 1)[0]
if len(prefix.strip()) < 100 or "Optional Jev-on advisory" in prefix:
    raise SystemExit(1)
PY
	done
}

verify_core_composition() {
	local target=$1 evidence_dir=$2 command_id
	mkdir -p "$evidence_dir" || return 1
	[ ! -d "$target/.specify/presets/$PRESET_ID" ] || return 1
	preset_registered_at "$target" && return 1
	for command_id in "${COMMANDS[@]}"; do
		(cd "$target" && specify preset resolve "$command_id") >"$evidence_dir/$command_id.resolve" 2>&1 || return 1
		(cd "$target" && specify artifact info "$command_id" --json) >"$evidence_dir/$command_id.json" 2>"$evidence_dir/$command_id.artifact-error" || return 1
		RESOLVE_FILE="$evidence_dir/$command_id.resolve" ARTIFACT_FILE="$evidence_dir/$command_id.json" COMMAND_ID="$command_id" TARGET="$target" python3 - <<'PY' || return 1
import json
import os
from pathlib import Path

resolve_text = Path(os.environ["RESOLVE_FILE"]).read_text(encoding="utf-8")
if "jev-seams" in resolve_text or "[append]" in resolve_text or "core" not in resolve_text:
    raise SystemExit(1)
stack = json.loads(Path(os.environ["ARTIFACT_FILE"]).read_text(encoding="utf-8")).get("stack")
if not isinstance(stack, list) or any(row.get("presetId") == "jev-seams" for row in stack):
    raise SystemExit(1)
if not any(row.get("layer") is None and row.get("strategy") == "replace" for row in stack):
    raise SystemExit(1)
prompt = Path(os.environ["TARGET"]) / ".pi" / "prompts" / f"{os.environ['COMMAND_ID']}.md"
text = prompt.read_text(encoding="utf-8")
if not text.startswith("---\n") or "Optional Jev-on advisory" in text:
    raise SystemExit(1)
PY
	done
}

# Uninstall remains available as the recovery path even if the tracker has
# since been disabled. It still requires SpecKit so reconciliation is supported.
if [ ! -d "$SPECIFY_DIR" ]; then
	preflight_failure "target project" "missing $SPECIFY_DIR" "initialize SpecKit in the target project"
fi
command -v specify >/dev/null 2>&1 ||
	preflight_failure "SpecKit CLI" "specify not found on PATH" "install SpecKit 1.0.12"
SPECIFY_VERSION="$(specify --version 2>/dev/null)"
specify_status=$?
[ "$specify_status" -eq 0 ] || preflight_failure "SpecKit CLI" "specify --version exit $specify_status" "install SpecKit 1.0.12"
case "$SPECIFY_VERSION" in
	"specify $REQ_SPECIFY"|"$REQ_SPECIFY") : ;;
	*) preflight_failure "SpecKit resolver compatibility" "$SPECIFY_VERSION" "install SpecKit 1.0.12" ;;
esac

STAGE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/jev-speckit-install.XXXXXX")" ||
	preflight_failure "staging" "could not create temporary staging directory" "check temporary-directory permissions"

if [ "$UNINSTALL" -eq 1 ]; then
	capture_active_state || preflight_failure "rollback snapshot" "could not snapshot the preset registry" "check project permissions and retry"
	ACTIVATION_STARTED=1
	reconcile_without_jev "$PROJECT" || activation_failure "specify preset removal/reconciliation failed"
	verify_core_composition "$PROJECT" "$STAGE_DIR/uninstall-evidence" ||
		activation_failure "uninstall did not resolve all four commands without jev-seams"
	# Remove backup data left by versions of this installer that predated the
	# resolver-owned rollback contract. Generated prompts are never read from it.
	rm -rf "$SPECIFY_DIR/.jev-seams-install-backup" || activation_failure "could not remove obsolete installer backup state"
	ACTIVATION_STARTED=0
	INSTALL_COMPLETE=1
	info "removed project-local $PRESET_ID preset and reconciled all four commands from remaining layers"
	exit 0
fi

# Installation preflight: tracker, project capabilities, exact source manifest,
# and an isolated resolver/reconciliation/introspection rehearsal.
[ -f "$TRACKER_ACTIVE/index.js" ] ||
	preflight_failure "active tracker" "missing $TRACKER_ACTIVE/index.js" "activate Jev-on tracking before requesting SpecKit seams"
[ "$(readlink -f "$TRACKER_ACTIVE")" = "$(readlink -f "$TRACKER_SOURCE")" ] ||
	preflight_failure "active tracker" "active tracker path does not resolve the suite tracker" "rerun scripts/install.sh --jev-on before installing SpecKit seams"

[ -s "$SPECIFY_DIR/memory/constitution.md" ] ||
	preflight_failure "live constitution" "missing or empty .specify/memory/constitution.md" "initialize or repair the target SpecKit constitution"
[ -d "$SPECIFY_DIR/scripts" ] ||
	preflight_failure "project-local SpecKit scripts" "missing .specify/scripts" "initialize or upgrade SpecKit in the target project"
[ -d "$PROMPTS_DIR" ] ||
	preflight_failure "project-local command artifacts" "missing .pi/prompts" "install or upgrade the Pi SpecKit integration"
for command_id in "${COMMANDS[@]}"; do
	[ -f "$PROMPTS_DIR/$command_id.md" ] ||
		preflight_failure "project-local command artifacts" "missing .pi/prompts/$command_id.md" "reconcile all four core SpecKit commands before enabling Jev seams"
done
[ -f "$PRESET_SOURCE/preset.yml" ] ||
	preflight_failure "preset source" "missing $PRESET_SOURCE/preset.yml" "restore the jev-seams preset source"
check_source_manifest ||
	preflight_failure "preset source" "manifest is not the exact four-command append set" "repair and validate the complete jev-seams preset"

if [ "${JEV_SPECKIT_TEST_SUBSET:-0}" = 1 ]; then
	preflight_failure "all-or-none command set" "requested subset of the four SpecKit seams" "install all four commands together or leave all four disabled"
fi

STAGED_PROJECT="$STAGE_DIR/project"
mkdir -p "$STAGED_PROJECT/.pi/prompts" || preflight_failure "staging" "could not stage target integration" "check temporary-directory permissions"
cp -a "$SPECIFY_DIR" "$STAGED_PROJECT/.specify" ||
	preflight_failure "staging" "could not stage .specify" "check target readability and temporary-directory permissions"
if [ -d "$STAGED_PROJECT/.specify/presets/$PRESET_ID" ] || preset_registered_at "$STAGED_PROJECT"; then
	(cd "$STAGED_PROJECT" && specify preset remove "$PRESET_ID") >"$STAGE_DIR/staged-remove.out" 2>&1 ||
		preflight_failure "preset resolver capability" "could not remove the staged prior preset" "repair the project preset registry"
fi
(cd "$STAGED_PROJECT" && specify preset add --dev "$PRESET_SOURCE") >"$STAGE_DIR/staged-add.out" 2>&1 ||
	preflight_failure "preset resolver capability" "specify preset add --dev failed in staging" "upgrade SpecKit or repair the project preset registry"
verify_composition "$STAGED_PROJECT" "$STAGE_DIR/staged-evidence" ||
	preflight_failure "preset composition/introspection" "one or more staged commands lacked exact core-plus-one-append evidence" "upgrade SpecKit or repair the target Pi integration"
info "preflight: staged and verified the exact four-command core-plus-append composition"

# Active transaction. Only the preset registry is snapshotted; generated
# command artifacts are always regenerated by SpecKit from remaining layers.
capture_active_state || preflight_failure "rollback snapshot" "could not snapshot the preset registry" "check project permissions and retry"
ACTIVATION_STARTED=1
if [ -d "$ACTIVE_PRESET" ] || preset_registered_at "$PROJECT"; then
	(cd "$PROJECT" && specify preset remove "$PRESET_ID") >"$STAGE_DIR/active-remove.out" 2>&1 ||
		activation_failure "could not remove the prior jev-seams preset"
fi
(cd "$PROJECT" && specify preset add --dev "$PRESET_SOURCE") >"$STAGE_DIR/active-add.out" 2>&1 ||
	activation_failure "specify preset add --dev failed"

if [ "${JEV_SPECKIT_FAIL_AFTER_PRESET:-0}" = 1 ]; then
	activation_failure "injected failure after preset activation"
fi

verify_composition "$PROJECT" "$STAGE_DIR/active-evidence" ||
	activation_failure "active resolver/artifact verification failed for the four-command set"
ACTIVATION_STARTED=0
INSTALL_COMPLETE=1
info "installed and verified project-local $PRESET_ID for all four SpecKit commands"
