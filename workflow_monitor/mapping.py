"""Normalize private reader rows into a closed workflow graph.

This is deliberately a pure boundary: it parses only the recording contract and does
not consult progress rows to fill gaps in recorded history.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .lineage import resolve

KNOWN_KINDS = frozenset({"started", "returned", "passed", "failed", "interrupted", "question_requested", "answer_returned", "answer_sent", "delivery_failed", "abandoned", "gap"})
KNOWN_PHASES = frozenset({"prepare", "gate", "worker", "check", "checkpoint", "review", "terminal"})


def _object(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    try:
        decoded = json.loads(value)
    except (TypeError, ValueError):
        return None
    return decoded if isinstance(decoded, dict) else None


def _valid_facts(facts: dict[str, Any]) -> bool:
    allowed = {"role", "parent_occurrence_id", "error_category", "ordinal", "exit_code", "baseline", "head",
               "no_change", "review_base", "review_head", "approved", "finding_count", "recording_gap"}
    if set(facts) - allowed:
        return False
    return (not isinstance(facts.get("role"), (list, dict)) and
            ("ordinal" not in facts or type(facts["ordinal"]) is int) and
            ("exit_code" not in facts or type(facts["exit_code"]) is int) and
            ("finding_count" not in facts or type(facts["finding_count"]) is int) and
            ("no_change" not in facts or type(facts["no_change"]) is bool) and
            ("approved" not in facts or type(facts["approved"]) is bool))


def _descriptor(row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return only a complete, closed declared plan; never repair a partial one."""
    description = _object(row.get("description"))
    if description is None or description.get("version") != 1:
        return None, "description_invalid"
    phases, tasks = description.get("phases"), description.get("tasks")
    if not isinstance(phases, list) or not isinstance(tasks, list) or not tasks:
        return None, "description_invalid"
    phase_ids = [phase.get("id") for phase in phases if isinstance(phase, dict)]
    if (len(phase_ids) != len(phases) or any(not isinstance(value, str) or not value for value in phase_ids) or
            len(set(phase_ids)) != len(phase_ids) or phase_ids.count("review") != 1):
        return None, "description_invalid"
    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if (len(task_ids) != len(tasks) or any(not isinstance(value, str) or not value for value in task_ids) or
            len(set(task_ids)) != len(task_ids)):
        return None, "description_invalid"
    dependencies = {task["id"]: task.get("depends") for task in tasks}
    if any(not isinstance(values, list) or any(not isinstance(value, str) or value not in dependencies or value == task_id
                                                for value in values) or len(set(values)) != len(values)
           for task_id, values in dependencies.items()):
        return None, "description_invalid"
    remaining = {task_id: set(values) for task_id, values in dependencies.items()}
    while remaining:
        ready = {task_id for task_id, values in remaining.items() if not values}
        if not ready:
            return None, "description_invalid"
        for task_id in ready:
            del remaining[task_id]
        for values in remaining.values():
            values.difference_update(ready)
    return description, None


def normalize(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return graph facts while retaining malformed/unknown rows as such.

    The returned values are still private internal facts.  Call ``public.minimize``
    before presenting anything to a browser.
    """
    state = snapshot.get("state") if isinstance(snapshot, dict) else "unavailable"
    if state != "ok":
        return {"state": state if isinstance(state, str) else "unavailable", "code": snapshot.get("code"),
                "runs": [], "observations": [], "occurrences": [], "phases": [], "tasks": [], "edges": [],
                "unknown_records": []}

    runs: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    descriptions: dict[str, dict[str, Any]] = {}
    for row in snapshot.get("runs", []):
        if not isinstance(row, dict) or not isinstance(row.get("run_id"), str):
            continue
        run_id = row["run_id"]
        retained_description = _object(row.get("description"))
        description, incomplete = _descriptor(row)
        runs.append({"run_id": run_id, "started_at": row.get("started_at"),
                     "description": retained_description, "plan_available": description is not None,
                     "incomplete": incomplete})
        if description is None:
            unknown.append({"run_id": run_id, "seq": None, "code": incomplete})
            continue
        descriptions[run_id] = description
        for phase in description["phases"]:
            if not isinstance(phase, dict) or not isinstance(phase.get("id"), str):
                unknown.append({"run_id": run_id, "seq": None, "code": "phase_invalid"})
                continue
            phase_id = phase["id"]
            phases.append({"run_id": run_id, "phase_id": phase_id, "label": phase.get("label"),
                           "pre_recording": phase.get("pre_recording"), "possible_branches": phase.get("possible_branches")})
            if isinstance(phase.get("possible_branches"), list):
                for target in phase["possible_branches"]:
                    if isinstance(target, str):
                        edges.append({"run_id": run_id, "type": "possible_flow", "from": ("phase", phase_id),
                                      "to": ("phase", target)})
        for task in description["tasks"]:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                unknown.append({"run_id": run_id, "seq": None, "code": "task_invalid"})
                continue
            task_id = task["id"]
            tasks.append({"run_id": run_id, "task_id": task_id, "label": task.get("label"), "summary": task.get("summary"),
                          "depends": task.get("depends")})
            if isinstance(task.get("depends"), list):
                for prerequisite in task["depends"]:
                    if isinstance(prerequisite, str):
                        edges.append({"run_id": run_id, "type": "task_prerequisite", "from": ("task", prerequisite),
                                      "to": ("task", task_id)})

    previous: dict[str, int] = {}
    occurrence_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    known_runs = {run["run_id"] for run in runs}
    for row in snapshot.get("observations", []):
        if not isinstance(row, dict) or row.get("run_id") not in known_runs or type(row.get("seq")) is not int:
            continue
        run_id, seq = row["run_id"], row["seq"]
        facts = _object(row.get("facts"))
        valid = (isinstance(row.get("occurrence_id"), str) and row.get("phase") in KNOWN_PHASES and
                 row.get("kind") in KNOWN_KINDS and facts is not None and _valid_facts(facts))
        if not valid:
            unknown.append({"run_id": run_id, "seq": seq, "code": "unsupported_observation"})
            continue
        observation = {"run_id": run_id, "seq": seq, "occurrence_id": row["occurrence_id"], "phase": row["phase"],
                       "task_id": row.get("task_id") if isinstance(row.get("task_id"), str) else None,
                       "kind": row["kind"], "recorded_at": row.get("recorded_at"), "facts": facts}
        observations.append(observation)
        occurrence_rows[(run_id, row["occurrence_id"])].append(observation)
        if run_id in previous:
            edges.append({"run_id": run_id, "type": "recorded_next", "from": ("observation", previous[run_id]),
                          "to": ("observation", seq)})
        previous[run_id] = seq

    occurrences = []
    for (run_id, occurrence_id), rows in occurrence_rows.items():
        first, last = rows[0], rows[-1]
        occurrences.append({"run_id": run_id, "occurrence_id": occurrence_id, "phase": first["phase"],
                            "task_id": first["task_id"], "observations": rows, "incomplete":
                            not any(row["kind"] in {"passed", "failed", "interrupted", "abandoned"} for row in rows)})
        edges.append({"run_id": run_id, "type": "phase_occurrence", "from": ("phase", first["phase"]),
                      "to": ("occurrence", occurrence_id)})
        for row in rows:
            edges.append({"run_id": run_id, "type": "execution_milestone", "from": ("occurrence", occurrence_id),
                          "to": ("observation", row["seq"])})
            if row["phase"] == "review" and "review_base" in row["facts"] and "review_head" in row["facts"]:
                edges.append({"run_id": run_id, "type": "reviewed_range", "from": ("occurrence", occurrence_id),
                              "to": ("observation", row["seq"])})
    followups, review_acceptance = resolve(runs, occurrences)
    return {"state": "ok", "runs": runs, "phases": phases, "tasks": tasks, "occurrences": occurrences,
            "observations": observations, "edges": edges, "unknown_records": unknown,
            "unsupported_run_ids": list(snapshot.get("unsupported_run_ids", [])), "followups": followups,
            "review_acceptance": review_acceptance}


__all__ = ["normalize"]
