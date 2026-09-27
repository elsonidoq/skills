#!/usr/bin/env bash
# Install/verify the pi skill suite: requirements first, then discoverability.
#
# What it does:
#   1. Requires pi (auto-installs pinned packages if missing)
#   2. Makes the suite skills discoverable via the user `skills` setting
#   3. Sanity-checks collision candidates and optional deps
#   4. Runs the deterministic suite lint (and, with --probe, one model call
#      that proves pi loads the suite without warnings)
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
SKILLS_ENTRY="$SUITE_DIR/skills"
AGENTS_SKILLS="$HOME/.agents/skills"

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

# Ensure skill discovery is configured before touching anything else.
mkdir -p "$AGENT_DIR"

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

# ---- 4. Collision guard ----------------------------------------------------
for f in "$AGENTS_SKILLS"/*/SKILL.md; do
  [ -e "$f" ] || continue
  if grep -q '^name:[[:space:]]*use-railway' "$f" 2>/dev/null; then
    fatal "skill collision: $f also declares name 'use-railway' — move it out of $AGENTS_SKILLS (e.g. ~/.agents/backups/)"
  fi
done

# ---- 5. Make suite skills discoverable ---------------------------------------
python3 - "$SETTINGS" "$SKILLS_ENTRY" <<'PY'
import json, os, sys
path, entry = sys.argv[1], os.path.abspath(sys.argv[2])
changed = {}
if os.path.exists(path):
    data = json.load(open(path))
else:
    data = {}
skills = data.get("skills")
if skills is None:
    data["skills"] = [entry]; changed["skills"] = "added"
elif entry not in skills:
    data["skills"] = skills + [entry]; changed["skills"] = "appended"
for k, v in changed.items():
    print(f"==> settings: {k} {v}")
if changed or not os.path.exists(path):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)
    print(f"==> wrote {path}")
else:
    print(f"==> settings ok: {path}")
PY
[ -d "$SKILLS_ENTRY" ] || fatal "suite skills directory missing: $SKILLS_ENTRY"

# ---- 6. Static validation -----------------------------------------------------
info "running suite lint"
"$SUITE_DIR/scripts/check-skills-lint.sh" || fatal "suite lint failed"

# ---- 7. Optional end-to-end probe --------------------------------------------
if [ "$PROBE" = 1 ]; then
  info "running headless pi probe (one model call)"
  "$SUITE_DIR/scripts/probe-pi-load.sh" || fatal "pi probe failed"
fi

printf '\n==> Done. Run `/reload` inside pi (or start a new session) so the skills setting is picked up.\n'