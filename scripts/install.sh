#!/usr/bin/env bash
# Install/verify the pi skill suite. Manual mode is the default; --jev-on
# transactionally enables the measured Jev tracker and four guarded seams.
set -uo pipefail

SUITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
SETTINGS="$AGENT_DIR/settings.json"
REQ_PI="0.87"
REQ_JEV="0.6.3"
PKG_SUBAGENTS="npm:pi-subagents@0.73.1"
PKG_ASKUSER="npm:pi-ask-user@0.15.1"
SKILLS_DIR="$SUITE_DIR/skills"
AGENTS_SKILLS="$HOME/.agents/skills"
AGENTS_BACKUPS="$HOME/.agents/backups"
TRACKER_SOURCE="$SUITE_DIR/extensions/jev-metrics"
TRACKER_ACTIVE="$AGENT_DIR/extensions/jev-metrics"
JEV_STATE_DIR="$AGENT_DIR/jev-metrics"
GLOBAL_SEAMS_ACTIVE="$JEV_STATE_DIR/global-seams-enabled"
SPECKIT_INSTALLER="$SUITE_DIR/scripts/install-jev-speckit.sh"
GLOBAL_SEAMS='scientific-method-debugging
receiving-code-review
coordinate-implementation
track-open-issue'

PROBE=0
JEV_ON=0
SPECKIT_PROJECT=
while [ "$#" -gt 0 ]; do
	case "$1" in
		--probe) PROBE=1 ;;
		--jev-on) JEV_ON=1 ;;
		--speckit-project)
			shift
			[ "$#" -gt 0 ] || { printf '%s\n' "usage: $0 [--probe] [--jev-on [--speckit-project DIR]]" >&2; exit 2; }
			SPECKIT_PROJECT=$1
			;;
		-h|--help)
			printf '%s\n' "usage: $0 [--probe] [--jev-on [--speckit-project DIR]]"
			exit 0
			;;
		*) printf '%s\n' "usage: $0 [--probe] [--jev-on [--speckit-project DIR]]" >&2; exit 2 ;;
	esac
	shift
done
if [ -n "$SPECKIT_PROJECT" ] && [ "$JEV_ON" -ne 1 ]; then
	printf '%s\n' "ERROR: --speckit-project requires --jev-on" >&2
	exit 2
fi

info() { printf '==> %s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fatal() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

STAGE_DIR=
ACTIVATION_STARTED=0
INSTALL_COMPLETE=0
TRACKER_WAS_PRESENT=0
SEAMS_WERE_PRESENT=0
EXTENSIONS_DIR_WAS_PRESENT=0
STATE_DIR_WAS_PRESENT=0
MARKER_TMP=

rollback_activation() {
	[ "$ACTIVATION_STARTED" -eq 1 ] || return 0
	rollback_ok=1
	rm -rf "$TRACKER_ACTIVE" "$GLOBAL_SEAMS_ACTIVE" || rollback_ok=0
	[ -z "$MARKER_TMP" ] || rm -f "$MARKER_TMP" || rollback_ok=0
	if [ "$TRACKER_WAS_PRESENT" -eq 1 ]; then
		mkdir -p "$(dirname "$TRACKER_ACTIVE")" || rollback_ok=0
		cp -a "$STAGE_DIR/rollback/tracker" "$TRACKER_ACTIVE" || rollback_ok=0
	fi
	if [ "$SEAMS_WERE_PRESENT" -eq 1 ]; then
		mkdir -p "$(dirname "$GLOBAL_SEAMS_ACTIVE")" || rollback_ok=0
		cp -a "$STAGE_DIR/rollback/global-seams-enabled" "$GLOBAL_SEAMS_ACTIVE" || rollback_ok=0
	fi
	if [ "$STATE_DIR_WAS_PRESENT" -eq 0 ]; then rmdir "$JEV_STATE_DIR" 2>/dev/null || :; fi
	if [ "$EXTENSIONS_DIR_WAS_PRESENT" -eq 0 ]; then rmdir "$(dirname "$TRACKER_ACTIVE")" 2>/dev/null || :; fi
	ACTIVATION_STARTED=0
	if [ "$rollback_ok" -eq 1 ]; then
		printf '%s\n' "Rollback: restored pre-activation tracker and seam state." >&2
		return 0
	fi
	printf '%s\n' "Rollback: incomplete; inspect $TRACKER_ACTIVE and $GLOBAL_SEAMS_ACTIVE before retrying." >&2
	return 1
}

cleanup() {
	if [ "$ACTIVATION_STARTED" -eq 1 ] && [ "$INSTALL_COMPLETE" -ne 1 ]; then
		rollback_activation
	fi
	[ -z "$STAGE_DIR" ] || rm -rf "$STAGE_DIR"
}
trap cleanup EXIT

preflight_failure() {
	printf '%s\n' "ERROR: Jev-on preflight failed: $1" >&2
	printf '%s\n' "Observed: $2" >&2
	printf '%s\n' "Resolution: $3" >&2
	printf '%s\n' "No optimized seam was enabled." >&2
	exit 1
}

activation_failure() {
	reason=$1
	printf '%s\n' "ERROR: Jev-on activation failed: $reason" >&2
	printf '%s\n' "Observed: $reason" >&2
	printf '%s\n' "Resolution: resolve the active-path conflict or permission failure, then rerun --jev-on" >&2
	if rollback_activation; then
		printf '%s\n' "No optimized seam was enabled." >&2
	else
		printf '%s\n' "Optimized seam state could not be confirmed; manual recovery is required." >&2
	fi
	exit 1
}

# Execute the tracker factory against a minimal fake ExtensionAPI and require
# the exact public registrations. The harness never invokes Jev.
check_tracker_registration() {
	tracker_entry=$1
	phase=$2
	JEV_TRACKER_CHECK=$phase node --input-type=module - "$tracker_entry" <<'NODE'
import { pathToFileURL } from "node:url";
const entry = process.argv[2];
const tools = [];
const commands = [];
const api = {
	on() {},
	appendEntry() {},
	registerTool(tool) {
		if (tools.includes(tool.name)) throw new Error("duplicate tool");
		tools.push(tool.name);
	},
	registerCommand(name) {
		if (commands.includes(name)) throw new Error("duplicate command");
		commands.push(name);
	},
};
const loaded = await import(pathToFileURL(entry));
if (typeof loaded.default !== "function") process.exit(10);
await loaded.default(api);
const expectedTools = ["jev_disposition", "jev_metrics", "jev_rank"];
if (JSON.stringify(tools.sort()) !== JSON.stringify(expectedTools)) process.exit(11);
if (JSON.stringify(commands.sort()) !== JSON.stringify(["jev-metrics"])) process.exit(12);
NODE
}

# ---- 1. Requirements -------------------------------------------------------
if ! command -v pi >/dev/null 2>&1; then
	if [ "$JEV_ON" -eq 1 ]; then
		preflight_failure "Pi compatibility" "pi not found on PATH" "install Pi 0.87.x (tested 0.87.1)"
	fi
	fatal "pi not found on PATH — install it first (see https://pi.dev/install)"
fi
PI_VERSION="$(pi --version 2>/dev/null)"
info "pi $PI_VERSION"
case "$PI_VERSION" in
	"$REQ_PI".*|"$REQ_PI") : ;;
	*) warn "suite pins pi 0.87.x (tested 0.87.1); found $PI_VERSION — version-specific wording may drift" ;;
esac
command -v python3 >/dev/null 2>&1 || fatal "python3 required (suite scripts and this installer use it)"

# ---- 2. Pinned packages ----------------------------------------------------
installed_pkgs="$(pi list 2>/dev/null)"
for pkg in "$PKG_SUBAGENTS" "$PKG_ASKUSER"; do
	if printf '%s\n' "$installed_pkgs" | grep -Fq "$pkg"; then
		info "package ok: $pkg"
	else
		info "installing $pkg"
		pi install "$pkg" || fatal "pi install $pkg failed"
		installed_pkgs="$(pi list 2>/dev/null)"
	fi
done

# ---- 3. Optional dependencies in manual mode ------------------------------
if [ ! -d "$AGENTS_SKILLS/jev" ]; then
	warn "'jev' skill not found at $AGENTS_SKILLS/jev — finish-session-jev triage will fall back to manual routing"
fi

# ---- 4. Discoverability via ~/.agents/skills ------------------------------
mkdir -p "$AGENTS_SKILLS" "$AGENTS_BACKUPS"
[ -d "$SKILLS_DIR" ] || fatal "suite skills directory missing: $SKILLS_DIR"

python3 - "$SKILLS_DIR" "$AGENTS_SKILLS" "$AGENTS_BACKUPS" "$SETTINGS" "$AGENT_DIR" <<'PY'
import json, os, sys, time

skills_dir, agents_skills, backups, settings_path, agent_dir = sys.argv[1:]
suite_skills = []
for name in sorted(os.listdir(skills_dir)):
    directory = os.path.join(skills_dir, name)
    if os.path.isfile(os.path.join(directory, "SKILL.md")):
        suite_skills.append((name, os.path.abspath(directory)))

linked = backed_up = existing_ok = 0
for name, src in suite_skills:
    dst = os.path.join(agents_skills, name)
    if os.path.islink(dst):
        if os.path.realpath(dst) == os.path.realpath(src):
            existing_ok += 1
            continue
        os.rename(dst, os.path.join(backups, f"{name}.{time.strftime('%Y%m%d%H%M%S')}"))
        os.symlink(src, dst)
        print(f"==> replaced symlink: ~/.agents/skills/{name} -> {src}")
        backed_up += 1
        continue
    if os.path.exists(dst) or os.path.islink(dst):
        os.rename(dst, os.path.join(backups, f"{name}.{time.strftime('%Y%m%d%H%M%S')}"))
        print(f"==> backed up conflicting entry: ~/.agents/skills/{name}")
        backed_up += 1
    if not os.path.exists(dst):
        os.symlink(src, dst)
        print(f"==> linked: ~/.agents/skills/{name} -> {src}")
        linked += 1

entry = os.path.realpath(skills_dir)
saved = False
if os.path.exists(settings_path):
    data = json.load(open(settings_path))
    skills = data.get("skills") or []
    kept = [s for s in skills if os.path.realpath(os.path.expanduser(s)) != entry]
    if len(kept) != len(skills):
        if kept:
            data["skills"] = kept
        else:
            data.pop("skills", None)
        tmp = settings_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, settings_path)
        print(f"==> settings: removed suite skills entry from {settings_path}")
        saved = True
if os.path.isdir(agent_dir) and not saved and not os.path.exists(settings_path):
    pass

print(f"==> suite skills: {len(suite_skills)} total ({linked} linked, {existing_ok} already ok, {backed_up} backed up)")
PY

# ---- 5. Static validation --------------------------------------------------
info "running suite lint"
"$SUITE_DIR/scripts/check-skills-lint.sh" || fatal "suite lint failed"

# Manual/default mode deliberately leaves the tracker and Jev-on marker absent.
if [ "$JEV_ON" -ne 1 ]; then
	if [ -L "$TRACKER_ACTIVE" ] && [ "$(readlink -f "$TRACKER_ACTIVE")" = "$(readlink -f "$TRACKER_SOURCE" 2>/dev/null || :)" ]; then
		rm -f "$TRACKER_ACTIVE"
	fi
	rm -f "$GLOBAL_SEAMS_ACTIVE"
	rmdir "$JEV_STATE_DIR" 2>/dev/null || :
	info "manual mode: tracker disabled; all four guarded global skills use their manual path"
else
	# ---- 6. Jev-on staging and complete preflight --------------------------
	mkdir -p "$AGENT_DIR"
	STAGE_DIR="$(mktemp -d "$AGENT_DIR/.jev-metrics-stage.XXXXXX")" || fatal "could not create Jev-on staging directory"
	mkdir -p "$STAGE_DIR/rollback" || fatal "could not initialize Jev-on staging directory"
	[ -d "$TRACKER_SOURCE" ] && [ -f "$TRACKER_SOURCE/index.js" ] ||
		preflight_failure "tracker load/registration" "tracker source missing" "restore extensions/jev-metrics and rerun the installer"
	cp -R "$TRACKER_SOURCE" "$STAGE_DIR/tracker" ||
		preflight_failure "tracker load/registration" "tracker staging failed" "check local filesystem permissions and retry"
	info "staged tracker without changing active paths"

	case "$PI_VERSION" in
		"$REQ_PI".*|"$REQ_PI") : ;;
		*) preflight_failure "Pi compatibility" "pi $PI_VERSION" "install Pi 0.87.x (tested 0.87.1)" ;;
	esac

	command -v node >/dev/null 2>&1 ||
		preflight_failure "Node runtime" "node not found on PATH" "install Node.js 22 or a proven compatible later runtime"
	NODE_VERSION="$(node --version 2>/dev/null)"
	node_numeric=${NODE_VERSION#v}
	node_major=${node_numeric%%.*}
	case "$node_major" in
		''|*[!0-9]*) preflight_failure "Node runtime" "node $NODE_VERSION" "install Node.js 22 or a proven compatible later runtime" ;;
		*) [ "$node_major" -ge 22 ] || preflight_failure "Node runtime" "node $NODE_VERSION" "install Node.js 22 or a proven compatible later runtime" ;;
	esac
	node -e 'require("node:test"); new Function("class RuntimeCheck { #field = 1; }");' >/dev/null 2>&1
	runtime_status=$?
	[ "$runtime_status" -eq 0 ] || preflight_failure "Node runtime" "runtime capability exit $runtime_status" "install Node.js 22 or a proven compatible later runtime"
	info "preflight: compatible Node runtime $NODE_VERSION"

	check_tracker_registration "$STAGE_DIR/tracker/index.js" preflight >/dev/null 2>&1
	tracker_status=$?
	[ "$tracker_status" -eq 0 ] || preflight_failure "tracker load/registration" "load harness exit $tracker_status" "repair the jev-metrics extension and rerun deterministic extension tests"
	info "preflight: tracker loads and registers the exact tools and command"

	command -v jev >/dev/null 2>&1 ||
		preflight_failure "Jev CLI compatibility" "jev not found on PATH" "install jev-cli 0.6.3"
	JEV_VERSION="$(jev --version 2>/dev/null)"
	jev_version_status=$?
	[ "$jev_version_status" -eq 0 ] || preflight_failure "Jev CLI compatibility" "jev --version exit $jev_version_status" "install jev-cli 0.6.3"
	case "$JEV_VERSION" in
		"jev $REQ_JEV"|"jev-cli $REQ_JEV"|"$REQ_JEV") : ;;
		*) preflight_failure "Jev CLI compatibility" "$JEV_VERSION" "install jev-cli 0.6.3" ;;
	esac
	info "preflight: compatible $JEV_VERSION"

	jev auth test >"$STAGE_DIR/jev-auth-test.out" 2>&1
	auth_status=$?
	[ "$auth_status" -eq 0 ] || preflight_failure "Jev authentication" "jev auth test exit $auth_status" "configure the Jev provider credentials and rerun jev auth test"
	info "preflight: jev auth test succeeded (provider output withheld)"

	node --test "$SUITE_DIR"/extensions/jev-metrics/test/*.test.js >"$STAGE_DIR/extension-tests.out" 2>&1
	test_status=$?
	[ "$test_status" -eq 0 ] || preflight_failure "deterministic checks" "extension test exit $test_status" "fix the deterministic extension tests before enabling Jev-on"
	bash -n "$SUITE_DIR/scripts/install.sh" "$SUITE_DIR/scripts/tests/test-install-jev.sh" >/dev/null 2>&1 &&
		sh -n "$SUITE_DIR/scripts/tests/lib/jev-install-fixtures.sh" >/dev/null 2>&1
	installer_check_status=$?
	[ "$installer_check_status" -eq 0 ] || preflight_failure "deterministic checks" "installer fixture syntax exit $installer_check_status" "fix the deterministic installer fixtures before enabling Jev-on"
	info "preflight: deterministic extension and installer checks passed"

	if [ -n "$SPECKIT_PROJECT" ] && [ ! -x "$SPECKIT_INSTALLER" ]; then
		preflight_failure "SpecKit installer" "scripts/install-jev-speckit.sh unavailable" "complete the project-local SpecKit installer or omit --speckit-project"
	fi

	# ---- 7. Transactional activation: tracker, verification, then seams ----
	[ -d "$(dirname "$TRACKER_ACTIVE")" ] && EXTENSIONS_DIR_WAS_PRESENT=1
	[ -d "$JEV_STATE_DIR" ] && STATE_DIR_WAS_PRESENT=1
	if [ -e "$TRACKER_ACTIVE" ] || [ -L "$TRACKER_ACTIVE" ]; then
		TRACKER_WAS_PRESENT=1
		cp -a "$TRACKER_ACTIVE" "$STAGE_DIR/rollback/tracker" || fatal "could not capture tracker rollback state"
	fi
	if [ -e "$GLOBAL_SEAMS_ACTIVE" ] || [ -L "$GLOBAL_SEAMS_ACTIVE" ]; then
		SEAMS_WERE_PRESENT=1
		cp -a "$GLOBAL_SEAMS_ACTIVE" "$STAGE_DIR/rollback/global-seams-enabled" || fatal "could not capture seam rollback state"
	fi
	ACTIVATION_STARTED=1

	mkdir -p "$(dirname "$TRACKER_ACTIVE")" || activation_failure "could not create Pi extension directory"
	rm -rf "$TRACKER_ACTIVE"
	ln -s "$TRACKER_SOURCE" "$TRACKER_ACTIVE" || activation_failure "could not activate tracker path"
	info "activated tracker: $TRACKER_ACTIVE"

	if [ "${JEV_INSTALL_FAIL_AFTER_TRACKER:-0}" = 1 ]; then
		activation_failure "injected failure after tracker activation"
	fi

	[ "$(readlink -f "$TRACKER_ACTIVE")" = "$(readlink -f "$TRACKER_SOURCE")" ] || activation_failure "active path does not resolve the staged tracker source"
	check_tracker_registration "$TRACKER_ACTIVE/index.js" active >/dev/null 2>&1
	active_tracker_status=$?
	[ "$active_tracker_status" -eq 0 ] || activation_failure "active tracker verification exit $active_tracker_status"
	info "verified active tracker path and registrations"

	mkdir -p "$JEV_STATE_DIR" || activation_failure "could not create Jev-on state directory"
	MARKER_TMP="$JEV_STATE_DIR/.global-seams-enabled.$$"
	printf '%s\n' "$GLOBAL_SEAMS" > "$MARKER_TMP" || activation_failure "could not stage global seam marker"
	mv -f "$MARKER_TMP" "$GLOBAL_SEAMS_ACTIVE" || activation_failure "could not activate all four global seams"
	MARKER_TMP=
	info "activated global seams: scientific-method-debugging, receiving-code-review, coordinate-implementation, track-open-issue"

	if [ -n "$SPECKIT_PROJECT" ]; then
		"$SPECKIT_INSTALLER" --project "$SPECKIT_PROJECT" || activation_failure "project-local SpecKit all-or-none handoff failed"
		info "activated project-local SpecKit seam set: $SPECKIT_PROJECT"
	fi
fi

# ---- 8. Optional end-to-end probe -----------------------------------------
if [ "$PROBE" -eq 1 ]; then
	info "running headless pi probe (one model call)"
	"$SUITE_DIR/scripts/probe-pi-load.sh" || fatal "pi probe failed"
fi

INSTALL_COMPLETE=1
if [ "$JEV_ON" -eq 1 ]; then
	printf '\n==> Jev-on installation complete. Start a new pi session or run `/reload` before using optimized seams.\n'
else
	printf '\n==> Manual installation complete. Start a new pi session or run `/reload` so suite skills are picked up.\n'
fi
