"""Read-only qualification of a recorded local runner identity.

The monitor deliberately rechecks the recorded identity rather than treating a PID or
fresh database read as progress.  It never signals or otherwise controls that process.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _identity(value: object) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    try:
        decoded = json.loads(value)
    except (TypeError, ValueError):
        return None
    if not isinstance(decoded, dict):
        return None
    if (type(decoded.get("pid")) is not int or decoded["pid"] <= 0 or
            not isinstance(decoded.get("start"), str) or not decoded["start"] or
            not isinstance(decoded.get("boot"), str) or not decoded["boot"] or
            type(decoded.get("uid")) is not int):
        return None
    return decoded


def _observed(pid: int) -> dict[str, Any] | None:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        fields = stat[stat.rindex(")") + 2:].split()
        return {"pid": pid, "start": fields[19], "uid": Path(f"/proc/{pid}").stat().st_uid,
                "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}
    except (OSError, ValueError, IndexError):
        return None


def qualify(value: object) -> dict[str, str | None]:
    """Return only a closed liveness result for a recorded identity.

    Identity parsing or inspection failures remain unknown; a live identity only says
    that the recorded process still exists, never that it made progress.
    """
    identity = _identity(value)
    if identity is None:
        return {"state": "unknown", "reason": "identity_unavailable"}
    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return {"state": "unknown", "reason": "identity_unverifiable"}
    if boot != identity["boot"]:
        return {"state": "stopped", "reason": "recorded_boot_changed"}
    if not Path(f"/proc/{identity['pid']}").exists():
        return {"state": "stopped", "reason": "process_absent"}
    observed = _observed(identity["pid"])
    if observed is None:
        return {"state": "unknown", "reason": "identity_unverifiable"}
    if all(observed[key] == identity[key] for key in ("pid", "start", "uid", "boot")):
        return {"state": "live", "reason": None}
    return {"state": "stopped", "reason": "identity_changed"}


__all__ = ["qualify"]
