#!/usr/bin/env bash
# Install/verify the pi skill suite: requirements first, then discoverability.
#
# What it does:
#   1. Requires pi (auto-installs pinned packages if missing)
#   2. Symlinks every suite skill into ~/.agents/skills (pi's standard scanned
#      location) and the spec-driven-development guidance into ~/.agents/docs,
#      retiring only proven suite-owned old links; foreign entries are preserved
#      and conflicts reported — no copies, the repo stays the single source of truth
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
AGENTS_DOCS="$HOME/.agents/docs"
AGENTS_BACKUPS="$HOME/.agents/backups"
SPEC_DRIVEN_GUIDANCE="$SUITE_DIR/docs/best_practices_spec_driven_development.md"

PROBE=0
case "${1:-}" in
  --workflow-prefix)
    { [ "$#" -eq 3 ] || [ "$#" -eq 4 ]; } || { echo "usage: $0 --workflow-prefix NEW_DIRECTORY --allow-network [--global]" >&2; exit 2; }
    shift
    prefix="$1"; shift
    exec "$SUITE_DIR/scripts/install-workflow.sh" --prefix "$prefix" "$@" ;;
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

# ---- 4. Discoverability via ~/.agents --------------------------------------
mkdir -p "$AGENTS_SKILLS" "$AGENTS_DOCS" "$AGENTS_BACKUPS"
[ -d "$SKILLS_DIR" ] || fatal "suite skills directory missing: $SKILLS_DIR"
[ -f "$SPEC_DRIVEN_GUIDANCE" ] || fatal "spec-driven guidance missing: $SPEC_DRIVEN_GUIDANCE"

python3 "$SUITE_DIR/scripts/install-links.py" \
  "$SKILLS_DIR" "$SPEC_DRIVEN_GUIDANCE" "$AGENTS_SKILLS" "$AGENTS_DOCS" \
  "$AGENTS_BACKUPS" "$SETTINGS" || fatal "skill link migration blocked; conflicting entries were preserved"

# ---- 5. Static validation -----------------------------------------------------
info "running suite lint"
"$SUITE_DIR/scripts/check-skills-lint.sh" || fatal "suite lint failed"

# ---- 6. Optional end-to-end probe --------------------------------------------
if [ "$PROBE" = 1 ]; then
  info "running headless pi probe (one model call)"
  "$SUITE_DIR/scripts/probe-pi-load.sh" || fatal "pi probe failed"
fi

printf '\n==> Done. Start a new pi session (or run `/reload`) so the new skills are picked up.\n'