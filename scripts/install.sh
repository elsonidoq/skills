#!/usr/bin/env bash
# Install/verify the pi skill suite: requirements first, then discoverability.
#
# What it does:
#   1. Requires pi (auto-installs pinned packages if missing)
#   2. Symlinks every suite skill into ~/.agents/skills (pi's standard scanned
#      location), backing up anything in the way — no copies, the repo stays
#      the single source of truth
#   3. Removes the old user-settings `skills` entry for this suite (kept in
#      sync with the ~/.agents/skills mechanism, no double registration)
#   4. Warns when optional deps (jev) are missing
#   5. Runs the deterministic suite lint; --probe adds a headless pi run that
#      asserts the suite skills are actually advertised in pi's system prompt
#
# Idempotent and safe to re-run. Usage:
#   scripts/install.sh [--probe]
#
# NOTE: SpecKit is a per-project toolkit and is intentionally NOT installed
# here; projects that use the pipeline install it themselves.
set -uo pipefail

SUITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
SETTINGS="$AGENT_DIR/settings.json"
REQ_PI="0.87"
PKG_SUBAGENTS="npm:pi-subagents@0.73.1"
PKG_ASKUSER="npm:pi-ask-user@0.15.1"
SKILLS_DIR="$SUITE_DIR/skills"
AGENTS_SKILLS="$HOME/.agents/skills"
AGENTS_BACKUPS="$HOME/.agents/backups"

PROBE=0
case "${1:-}" in
  --probe) PROBE=1 ;;
  "") ;;
  *) echo "usage: $0 [--probe]" >&2; exit 2 ;;
esac

info() { printf '==> %s\n' "$*"; }
warn()  { printf 'WARN: %s\n' "$*" >&2; }
fatal() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# ---- 1. Requirements -------------------------------------------------------
command -v pi >/dev/null 2>&1 || fatal "pi not found on PATH — install it first (see https://pi.dev/install)"
PI_VERSION="$(pi --version 2>/dev/null)"
info "pi $PI_VERSION"
case "$PI_VERSION" in
  "$REQ_PI".*|"$REQ_PI") : ;;
  *) warn "suite pins pi 0.87.x (tested 0.87.1); found $PI_VERSION — version-specific wording may drift" ;;
esac

command -v python3 >/dev/null 2>&1 || fatal "python3 required (suite scripts and this installer use it)"

# ---- 2. Pinned packages (auto-installed when missing) ----------------------
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

# ---- 3. Optional dependencies (warn only) ----------------------------------
if [ ! -d "$AGENTS_SKILLS/jev" ]; then
  warn "'jev' skill not found at $AGENTS_SKILLS/jev — finish-session-jev triage will fall back to manual routing"
fi

# ---- 4. Discoverability via ~/.agents/skills -------------------------------
mkdir -p "$AGENTS_SKILLS" "$AGENTS_BACKUPS"
[ -d "$SKILLS_DIR" ] || fatal "suite skills directory missing: $SKILLS_DIR"

python3 - "$SKILLS_DIR" "$AGENTS_SKILLS" "$AGENTS_BACKUPS" "$SETTINGS" "$AGENT_DIR" <<'PY'
import json, os, sys, time

skills_dir, agents_skills, backups, settings_path, agent_dir = sys.argv[1:]

suite_skills = []
for name in sorted(os.listdir(skills_dir)):
    d = os.path.join(skills_dir, name)
    if os.path.isfile(os.path.join(d, "SKILL.md")):
        suite_skills.append((name, os.path.abspath(d)))

linked = backed_up = existing_ok = 0
for name, src in suite_skills:
    dst = os.path.join(agents_skills, name)
    if os.path.islink(dst):
        if os.path.realpath(dst) == os.path.realpath(src):
            existing_ok += 1
            continue
        # stale/foreign symlink -> back up
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

# Remove the previous settings-based registration for this suite so pi does
# not discover the same skills twice (first-wins collision warning).
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
    pass  # nothing to clean

print(f"==> suite skills: {len(suite_skills)} total ({linked} linked, {existing_ok} already ok, {backed_up} backed up)")
PY

# ---- 5. Static validation -----------------------------------------------------
info "running suite lint"
"$SUITE_DIR/scripts/check-skills-lint.sh" || fatal "suite lint failed"

# ---- 6. Optional end-to-end probe --------------------------------------------
if [ "$PROBE" = 1 ]; then
  info "running headless pi probe (one model call)"
  "$SUITE_DIR/scripts/probe-pi-load.sh" || fatal "pi probe failed"
fi

printf '\n==> Done. Start a new pi session (or run `/reload`) so the new skills are picked up.\n'