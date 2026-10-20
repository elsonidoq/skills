"""Closed, best-effort monitoring records for new workflow runs.

This module deliberately stores only presentation-safe boundary facts.  It is not a
telemetry stream and failures in it must never affect the workflow it observes.
"""
from __future__ import annotations

import json
import sys
import time
import uuid

RECORDING_VERSION = 1
PHASES = frozenset({"prepare", "gate", "worker", "check", "checkpoint", "review", "terminal"})
KINDS = frozenset({"started", "returned", "passed", "failed", "interrupted", "question_requested", "answer_returned", "answer_sent", "delivery_failed", "abandoned"})
FACTS = frozenset({"role", "ordinal", "exit_code", "baseline", "head", "no_change", "approved", "finding_count", "parent_occurrence_id", "error_category", "review_base", "review_head"})


def _warn(message):
    print("coherence monitoring: " + message, file=sys.stderr, flush=True)


def _label(value, fallback):
    return value if isinstance(value, str) and 0 < len(value) <= 80 else fallback


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
                      "summary": _label(item.get("executive_summary"), "Task execution")})
    correction = monitor.get("correction_of") if isinstance(monitor, dict) else None
    if not (isinstance(correction, dict) and isinstance(correction.get("run_id"), str) and isinstance(correction.get("review_execution_id"), str)):
        correction = None
    requested = {k: executor.get(k) for k in ("provider", "model", "effort")} if isinstance(executor, dict) else {}
    return {"version": RECORDING_VERSION, "phases": ["prepare", "gate", "worker", "check", "checkpoint", "review", "terminal"],
            "tasks": tasks, "requested_executor": requested, "correction_of": correction,
            "runtime_revision": revision if isinstance(revision, str) else None,
            "runtime_revision_reason": None if isinstance(revision, str) else "unknown"}


class Recorder:
    """Optional append-only recorder. Every public method is safe to call on errors."""
    def __init__(self, store, run):
        self.store, self.run, self.registered = store, run, False

    def register(self, description):
        try:
            self.store.register_monitor_run(self.run, description)
            self.registered = True
            return True
        except Exception:
            _warn("recording registration unavailable")
            return False

    def occurrence(self):
        return uuid.uuid4().hex

    def emit(self, occurrence_id, phase, kind, *, task_id=None, facts=None):
        if not self.registered:
            return None
        try:
            if not isinstance(occurrence_id, str) or not occurrence_id or phase not in PHASES or kind not in KINDS:
                raise ValueError("closed monitoring fact rejected")
            if task_id is not None and not isinstance(task_id, str):
                raise ValueError("closed monitoring task rejected")
            facts = facts or {}
            if not isinstance(facts, dict) or set(facts) - FACTS or any(isinstance(v, (dict, list, bytes)) for v in facts.values()):
                raise ValueError("closed monitoring payload rejected")
            return self.store.append_monitor_observation(self.run, occurrence_id, phase, task_id, kind, facts)
        except Exception:
            _warn("recording append unavailable")
            return None


def now():
    return time.time()
