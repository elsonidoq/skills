"""Closed, best-effort monitoring records for new workflow runs.

This module deliberately stores only presentation-safe boundary facts.  It is not a
telemetry stream and failures in it must never affect the workflow it observes.
"""
from __future__ import annotations

import re
import sys
import time
import uuid

RECORDING_VERSION = 1
PHASES = frozenset({"prepare", "gate", "worker", "check", "checkpoint", "review", "terminal"})
KINDS = frozenset({"started", "returned", "passed", "failed", "interrupted", "question_requested", "answer_returned", "answer_sent", "delivery_failed", "abandoned"})
_HASH = re.compile(r"^[0-9a-f]{40,64}$")
_ROLES = frozenset({"worker", "fixing_worker", "reviewer"})
_ERRORS = frozenset({"blocked", "check", "git", "malformed", "transport", "interrupted", "unknown"})


def _warn(message):
    try:
        print("coherence monitoring: " + message, file=sys.stderr, flush=True)
    except Exception:
        pass


def _label(value, fallback, maximum=80):
    return value if isinstance(value, str) and 0 < len(value) <= maximum else fallback


def _sha(value):
    return isinstance(value, str) and bool(_HASH.fullmatch(value))


def _closed_facts(phase, kind, facts):
    """Validate the small phase/kind vocabulary before it reaches SQLite."""
    if not isinstance(facts, dict):
        return False
    allowed = {
        "prepare": {"error_category"},
        "gate": {"ordinal", "parent_occurrence_id", "error_category"},
        "worker": {"role", "parent_occurrence_id", "error_category"},
        "check": {"ordinal", "exit_code", "parent_occurrence_id", "error_category"},
        "checkpoint": {"baseline", "head", "no_change", "parent_occurrence_id", "error_category"},
        "review": {"role", "review_base", "review_head", "approved", "finding_count", "parent_occurrence_id", "error_category"},
        "terminal": {"baseline", "head", "error_category"},
    }[phase]
    if set(facts) - allowed:
        return False
    for key, value in facts.items():
        if key in {"baseline", "head", "review_base", "review_head"} and not _sha(value): return False
        if key == "role" and value not in _ROLES: return False
        if key in {"ordinal", "finding_count"} and (type(value) is not int or value < 0): return False
        if key == "exit_code" and (type(value) is not int): return False
        if key == "no_change" and type(value) is not bool: return False
        if key == "approved" and type(value) is not bool: return False
        if key == "parent_occurrence_id" and (not isinstance(value, str) or not value): return False
        if key == "error_category" and value not in _ERRORS: return False
    if kind in {"question_requested", "answer_returned", "answer_sent", "delivery_failed"}:
        return phase in {"gate", "worker", "review"} and "parent_occurrence_id" in facts
    if phase == "review" and kind in {"started", "passed", "failed", "interrupted", "returned"}:
        return facts.get("role") == "reviewer" and _sha(facts.get("review_base")) and _sha(facts.get("review_head"))
    if phase == "worker" and kind in {"started", "returned", "failed", "interrupted"}:
        return facts.get("role") in {"worker", "fixing_worker"}
    return True


def descriptor(contract, executor, revision=None):
    """Return a closed retained description; private task prose is never copied."""
    tasks = []
    monitor = contract.get("monitor") if isinstance(contract, dict) else None
    presentation = monitor.get("tasks", {}) if isinstance(monitor, dict) and isinstance(monitor.get("tasks"), dict) else {}
    for task in contract.get("tasks", []):
        item = presentation.get(task.get("id"), {}) if isinstance(presentation, dict) else {}
        item = item if isinstance(item, dict) else {}
        tasks.append({"id": task.get("id"), "depends": list(task.get("depends", [])),
                      "label": _label(item.get("label"), "Task"),
                      "summary": _label(item.get("executive_summary"), "Task execution", 240)})
    correction = monitor.get("correction_of") if isinstance(monitor, dict) else None
    if not (isinstance(correction, dict) and isinstance(correction.get("run_id"), str) and isinstance(correction.get("review_execution_id"), str)):
        correction = None
    requested = {k: executor.get(k) for k in ("provider", "model", "effort")} if isinstance(executor, dict) else {}
    return {"version": RECORDING_VERSION, "phases": ["prepare", "gate", "worker", "check", "checkpoint", "review", "terminal"],
            "tasks": tasks, "requested_executor": requested, "correction_of": correction,
            "runtime_revision": revision if _sha(revision) else None,
            "runtime_revision_reason": None if _sha(revision) else "unknown"}


class Recorder:
    """Optional append-only recorder. Every public method is safe to call on errors."""
    def __init__(self, store, run): self.store, self.run, self.registered = store, run, False

    def register(self, description):
        try:
            self.store.register_monitor_run(self.run, description)
            self.registered = True
            return True
        except Exception:
            _warn("recording registration unavailable")
            return False

    def occurrence(self):
        try:
            return uuid.uuid4().hex
        except Exception:
            _warn("recording occurrence unavailable")
            return None

    def emit(self, occurrence_id, phase, kind, *, task_id=None, facts=None):
        if not self.registered:
            return None
        try:
            facts = facts or {}
            if not isinstance(occurrence_id, str) or not occurrence_id or phase not in PHASES or kind not in KINDS or (task_id is not None and not isinstance(task_id, str)) or not _closed_facts(phase, kind, facts):
                raise ValueError("closed monitoring fact rejected")
            return self.store.append_monitor_observation(self.run, occurrence_id, phase, task_id, kind, facts)
        except Exception:
            _warn("recording append unavailable")
            return None


def now(): return time.time()
