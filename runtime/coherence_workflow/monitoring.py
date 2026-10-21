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
KINDS = frozenset({"started", "returned", "passed", "failed", "interrupted", "question_requested", "answer_returned", "answer_sent", "delivery_failed", "abandoned", "gap"})
_HASH = re.compile(r"^[0-9a-f]{40,64}$")
_ROLES = frozenset({"worker", "fixing_worker", "reviewer"})
_INVOCATION_KINDS = frozenset({"task_worker", "corrective_worker"})
_ERRORS = frozenset({"blocked", "check", "git", "malformed", "transport", "interrupted", "unknown"})
PHASE_DESCRIPTORS = (
    {"id": "intake", "label": "Task intake", "possible_branches": ["prepare", "terminal"], "pre_recording": True},
    {"id": "prepare", "label": "Task preparation", "possible_branches": ["gate", "worker", "terminal"], "pre_recording": False},
    {"id": "gate", "label": "Manual gate", "possible_branches": ["worker", "terminal"], "pre_recording": False},
    {"id": "worker", "label": "Task worker", "possible_branches": ["check", "terminal"], "pre_recording": False},
    {"id": "check", "label": "Project checks", "possible_branches": ["checkpoint", "terminal"], "pre_recording": False},
    {"id": "checkpoint", "label": "Focused checkpoint", "possible_branches": ["prepare", "review", "terminal"], "pre_recording": False},
    {"id": "review", "label": "Independent review", "possible_branches": ["terminal"], "pre_recording": False},
    {"id": "terminal", "label": "Run terminal", "possible_branches": [], "pre_recording": False},
)


def _warn(message):
    try:
        print("coherence monitoring: " + message, file=sys.stderr, flush=True)
    except Exception:
        pass


def _label(value, fallback, maximum=80):
    return value if isinstance(value, str) and 0 < len(value) <= maximum else fallback


def _sha(value):
    return isinstance(value, str) and bool(_HASH.fullmatch(value))


def _task_input(value):
    """One runner-selected checkpoint, never a viewer-inferred relation."""
    if not isinstance(value, dict) or set(value) != {"checkpoint_occurrence_id", "task_id", "producer_invocation_id", "correction_chain"}:
        return False
    if any(not isinstance(value[key], str) or not value[key] for key in
           ("checkpoint_occurrence_id", "task_id", "producer_invocation_id")):
        return False
    chain = value["correction_chain"]
    return (isinstance(chain, list) and chain and all(isinstance(item, str) and item for item in chain)
            and chain[-1] == value["producer_invocation_id"])


def _closed_facts(phase, kind, facts):
    """Validate the small phase/kind vocabulary before it reaches SQLite."""
    if not isinstance(facts, dict):
        return False
    if kind == "gap":
        return facts == {"recording_gap": True}
    allowed = {
        "prepare": {"error_category"},
        "gate": {"ordinal", "parent_occurrence_id", "error_category"},
        "worker": {"role", "execution_id", "trigger_execution_id", "predecessor_execution_id", "parent_occurrence_id", "error_category",
                   "invocation_id", "invocation_kind", "selected_input_checkpoints", "correction_chain",
                   "predecessor_invocation_id", "stopped_by_invocation_id", "support_invocation_id"},
        "check": {"ordinal", "exit_code", "execution_id", "parent_occurrence_id", "error_category"},
        "checkpoint": {"baseline", "head", "no_change", "execution_id", "parent_occurrence_id", "error_category",
                       "producer_invocation_id", "correction_chain"},
        "review": {"role", "execution_id", "review_ordinal", "trigger_execution_id", "predecessor_execution_id", "review_base", "review_head", "approved", "outcome", "finding_count", "parent_occurrence_id", "error_category"},
        "terminal": {"baseline", "head", "error_category", "stopped_by_invocation_id", "support_invocation_id"},
    }[phase]
    if set(facts) - allowed:
        return False
    for key, value in facts.items():
        if key in {"baseline", "head", "review_base", "review_head"} and not _sha(value): return False
        if key == "role" and value not in _ROLES: return False
        if key == "invocation_kind" and value not in _INVOCATION_KINDS: return False
        if key == "selected_input_checkpoints" and (not isinstance(value, list) or not all(_task_input(item) for item in value)): return False
        if key == "correction_chain" and (not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value)): return False
        if key in {"ordinal", "review_ordinal", "finding_count"} and (type(value) is not int or value < 0): return False
        if key == "exit_code" and type(value) is not int: return False
        if key == "no_change" and type(value) is not bool: return False
        if key == "approved" and type(value) is not bool: return False
        if key in {"execution_id", "trigger_execution_id", "predecessor_execution_id", "parent_occurrence_id", "invocation_id", "predecessor_invocation_id", "stopped_by_invocation_id", "support_invocation_id", "producer_invocation_id"} and (not isinstance(value, str) or not value): return False
        if key == "outcome" and value not in {"approved", "rejected", "failed", "interrupted"}: return False
        if key == "error_category" and value not in _ERRORS: return False
    if kind in {"question_requested", "answer_returned", "answer_sent", "delivery_failed"}:
        return phase in {"gate", "worker", "review"} and "parent_occurrence_id" in facts
    if phase == "review" and kind in {"started", "passed", "failed", "interrupted", "returned"}:
        return (facts.get("role") == "reviewer" and _sha(facts.get("review_base")) and
                _sha(facts.get("review_head")) and
                (("execution_id" not in facts and "review_ordinal" not in facts) or
                 (isinstance(facts.get("execution_id"), str) and type(facts.get("review_ordinal")) is int and facts["review_ordinal"] > 0)))
    if phase == "worker" and kind in {"started", "returned", "failed", "interrupted"}:
        if facts.get("role") not in {"worker", "fixing_worker"}:
            return False
        if not isinstance(facts.get("invocation_id"), str) or facts.get("invocation_kind") not in _INVOCATION_KINDS:
            return False
        chain = facts.get("correction_chain")
        if not isinstance(chain, list) or not chain or chain[-1] != facts["invocation_id"]:
            return False
        if "predecessor_invocation_id" in facts and (len(chain) < 2 or chain[-2] != facts["predecessor_invocation_id"]):
            return False
        if kind == "started":
            return "selected_input_checkpoints" in facts and "stopped_by_invocation_id" not in facts
        return "selected_input_checkpoints" in facts and (kind == "returned" or facts.get("stopped_by_invocation_id") == facts["invocation_id"])
    if phase == "checkpoint" and kind == "passed" and "producer_invocation_id" in facts:
        return isinstance(facts.get("correction_chain"), list) and facts["correction_chain"][-1] == facts["producer_invocation_id"]
    if phase == "terminal" and kind in {"failed", "interrupted"} and "stopped_by_invocation_id" in facts:
        return isinstance(facts["stopped_by_invocation_id"], str) and bool(facts["stopped_by_invocation_id"])
    return True
    return True


def descriptor(contract, executor, revision=None):
    """Return a closed retained description; private task prose is never copied."""
    try:
        return _descriptor(contract, executor, revision)
    except Exception:
        _warn("recording description unavailable")
        return {"version": RECORDING_VERSION, "description_version": 2, "phases": list(PHASE_DESCRIPTORS),
                "tasks": [], "requested_executor": {}, "correction_of": None,
                "runtime_revision": None, "runtime_revision_reason": "unknown"}


def _descriptor(contract, executor, revision=None):
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
    # This declares a closed vocabulary, not an executed review/fixing stage.
    return {"version": RECORDING_VERSION, "description_version": 2, "phases": list(PHASE_DESCRIPTORS),
            "tasks": tasks, "requested_executor": requested, "correction_of": correction,
            "runtime_revision": revision if _sha(revision) else None,
            "runtime_revision_reason": None if _sha(revision) else "unknown"}


class Recorder:
    """Optional append-only recorder. Every public method is safe to call on errors."""
    def __init__(self, store, run): self.store, self.run, self.registered, self.gap_pending = store, run, False, False

    def register(self, description, runner_identity=None):
        try:
            self.store.register_monitor_run(self.run, description, runner_identity)
            self.registered = True
            return True
        except Exception:
            _warn("recording registration unavailable")
            return False

    def occurrence(self):
        try:
            return uuid.uuid4().hex
        except Exception:
            # A later successful append records the missing optional boundary without
            # inventing its execution identity.
            self.gap_pending = True
            _warn("recording occurrence unavailable")
            return None

    def emit(self, occurrence_id, phase, kind, *, task_id=None, facts=None):
        if not self.registered:
            return None
        facts = facts or {}
        if (not isinstance(occurrence_id, str) or not occurrence_id or phase not in PHASES or
                kind not in KINDS or (task_id is not None and not isinstance(task_id, str)) or
                not _closed_facts(phase, kind, facts)):
            _warn("closed monitoring fact rejected")
            return None
        try:
            if self.gap_pending:
                self.store.append_monitor_observation(self.run, uuid.uuid4().hex, "terminal", None, "gap", {"recording_gap": True})
                self.gap_pending = False
            return self.store.append_monitor_observation(self.run, occurrence_id, phase, task_id, kind, facts)
        except Exception:
            self.gap_pending = True
            _warn("recording append unavailable")
            return None


def now(): return time.time()
