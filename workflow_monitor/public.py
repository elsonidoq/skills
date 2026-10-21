"""Closed public DTO construction for normalized monitor graphs."""
from __future__ import annotations

import hashlib
import re
from typing import Any

_HASH = re.compile(r"^[0-9a-f]{40,64}$")
_SAFE_ROLES = frozenset({"worker", "fixing_worker", "reviewer"})
_SAFE_KINDS = frozenset({"started", "returned", "passed", "failed", "interrupted", "question_requested", "answer_returned", "answer_sent", "delivery_failed", "abandoned", "gap"})


def _ref(kind: str, run: str, value: object = "") -> str:
    digest = hashlib.sha256((run + "\0" + str(value)).encode()).hexdigest()[:24]
    return f"{kind}_{digest}"


def run_ref(run_id: str) -> str:
    """Create the opaque public reference for a private run identity."""
    return _ref("run", run_id)


def _text(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _sha(value: object) -> str | None:
    return value if isinstance(value, str) and _HASH.fullmatch(value) else None


def _time(value: object) -> float | None:
    return value if type(value) in (int, float) else None


def _endpoint(run: str, endpoint: tuple[str, object]) -> str:
    kind, value = endpoint
    return _ref({"phase": "phase", "task": "task", "occurrence": "occ", "observation": "record"}.get(kind, "unknown"), run, value)


def minimize(graph: dict[str, Any]) -> dict[str, Any]:
    """Build public-only DTO data without forwarding any raw database row or payload."""
    if graph.get("state") != "ok":
        state = graph.get("state") if isinstance(graph.get("state"), str) else "unavailable"
        return {"monitor_version": 1, "state": state, "code": graph.get("code") if isinstance(graph.get("code"), str) else None,
                "runs": [], "phases": [], "tasks": [], "occurrences": [], "records": [], "edges": [],
                "unknown_records": [], "inventory": {"phase_count": 0, "occurrence_count": 0, "observation_count": 0,
                "supported_count": 0, "unsupported_count": 0, "hidden_count": 0}}

    public_runs = []
    for run in graph.get("runs", []):
        description = run.get("description") if isinstance(run.get("description"), dict) else {}
        requested = description.get("requested_executor") if isinstance(description.get("requested_executor"), dict) else {}
        public_runs.append({"ref": _ref("run", run["run_id"]), "display_id": run["run_id"], "label": "Recorded run", "started_at": _time(run.get("started_at")),
                            "description_version": description.get("description_version") if type(description.get("description_version")) is int else None,
                            "plan_availability": "complete" if run.get("plan_available") else "unavailable",
                            "requested_executor": {key: _text(requested.get(key), "unknown") for key in ("provider", "model", "effort")},
                            "completeness": "incomplete" if run.get("incomplete") else "recorded",
                            "review_acceptance": {key: (_sha(value) if key in {"base", "head"} else value)
                                                  for key, value in graph.get("review_acceptance", {}).get(run["run_id"], {"state": "unknown", "base": None, "head": None}).items()}})
    phases = [{"ref": _ref("phase", row["run_id"], row["phase_id"]), "run_ref": _ref("run", row["run_id"]),
               "phase_id": row["phase_id"], "label": _text(row.get("label"), row["phase_id"]), "pre_recording": row.get("pre_recording") is True}
              for row in graph.get("phases", [])]
    tasks = [{"ref": _ref("task", row["run_id"], row["task_id"]), "run_ref": _ref("run", row["run_id"]),
              "task_id": row["task_id"], "label": _text(row.get("label"), row["task_id"]), "summary": _text(row.get("summary"), "Task execution"),
              "prerequisite_refs": [_ref("task", row["run_id"], prerequisite) for prerequisite in row.get("depends", [])]}
             for row in graph.get("tasks", [])]
    review_definitions = [{"ref": _ref("review_definition", row["run_id"], row["phase_id"]),
                           "run_ref": _ref("run", row["run_id"]),
                           "phase_ref": _ref("phase", row["run_id"], row["phase_id"]),
                           "label": "Planned independent review — not an agent call."}
                          for row in graph.get("phases", []) if row.get("phase_id") == "review"]
    records = []
    for row in graph.get("observations", []):
        facts = row.get("facts") if isinstance(row.get("facts"), dict) else {}
        records.append({"ref": _ref("record", row["run_id"], row["seq"]), "run_ref": _ref("run", row["run_id"]),
                        "occurrence_ref": _ref("occ", row["run_id"], row["occurrence_id"]), "source_seq": row["seq"],
                        "kind": row["kind"] if row.get("kind") in _SAFE_KINDS else "unsupported", "recorded_at": _time(row.get("recorded_at")),
                        "ordinal": facts.get("ordinal") if type(facts.get("ordinal")) is int and facts["ordinal"] >= 0 else None,
                        "exit_code": facts.get("exit_code") if type(facts.get("exit_code")) is int else None,
                        "no_change": facts.get("no_change") if type(facts.get("no_change")) is bool else None,
                        "approved": facts.get("approved") if type(facts.get("approved")) is bool else None,
                        "finding_count": facts.get("finding_count") if type(facts.get("finding_count")) is int and facts["finding_count"] >= 0 else None,
                        "parent_occurrence_id": _text(facts.get("parent_occurrence_id")),
                        "error_category": facts.get("error_category") if isinstance(facts.get("error_category"), str) and facts.get("error_category") in {"blocked", "check", "git", "malformed", "transport", "interrupted", "unknown"} else None,
                        "recording_gap": facts.get("recording_gap") is True,
                        "baseline": _sha(facts.get("baseline")), "head": _sha(facts.get("head")),
                        "review_base": _sha(facts.get("review_base")), "review_head": _sha(facts.get("review_head"))})
    occurrences = []
    for row in graph.get("occurrences", []):
        first = row["observations"][0] if row.get("observations") else {}
        facts = first.get("facts") if isinstance(first.get("facts"), dict) else {}
        role = facts.get("role") if facts.get("role") in _SAFE_ROLES else "non_model"
        outcomes = [item.get("kind") for item in row.get("observations", [])]
        outcome = next((kind for kind in reversed(outcomes) if kind in {"passed", "failed", "interrupted", "abandoned"}), None)
        occurrences.append({"ref": _ref("occ", row["run_id"], row["occurrence_id"]), "run_ref": _ref("run", row["run_id"]),
                            "occurrence_id": row["occurrence_id"], "phase_ref": _ref("phase", row["run_id"], row["phase"]),
                            "task_ref": _ref("task", row["run_id"], row["task_id"]) if row.get("task_id") else None,
                            "role": role, "outcome": outcome, "completeness": "incomplete" if row.get("incomplete") else "complete",
                            "record_refs": [_ref("record", row["run_id"], item["seq"]) for item in row.get("observations", [])]})
    edges = [{"ref": _ref("edge", row["run_id"], f"{row['type']}:{row['from']}:{row['to']}"), "run_ref": _ref("run", row["run_id"]),
              "type": row["type"], "from_ref": _endpoint(row["run_id"], row["from"]), "to_ref": _endpoint(row["run_id"], row["to"]),
              "resolution": "recorded" if row["type"] not in {"possible_flow", "task_prerequisite"} else "declared"}
             for row in graph.get("edges", [])]
    unknown = [{"ref": _ref("unknown", item["run_id"], item["seq"] if type(item.get("seq")) is int else f"unknown_{index}"),
                "run_ref": _ref("run", item["run_id"]), "source_seq": item.get("seq") if type(item.get("seq")) is int else None,
                "code": item.get("code") if item.get("code") in {"description_invalid", "phase_invalid", "task_invalid", "unsupported_observation"} else "unsupported"}
               for index, item in enumerate(graph.get("unknown_records", []))]
    followups = [{"run_ref": _ref("run", row["run_id"]), "source_run_ref": _ref("run", row["source_run_id"]),
                  "review_occurrence_ref": _ref("occ", row["source_run_id"], row["review_occurrence_id"]),
                  "resolution": row["resolution"]}
                 for row in graph.get("followups", [])]
    inventory = {"phase_count": len(phases), "occurrence_count": len(occurrences), "observation_count": len(records),
                 "supported_count": len(records), "unsupported_count": len(unknown) + len(graph.get("unsupported_run_ids", [])), "hidden_count": 0}
    return {"monitor_version": 1, "state": "ok", "runs": public_runs, "phases": phases, "tasks": tasks,
            "review_definitions": review_definitions, "occurrences": occurrences, "records": records, "edges": edges,
            "unknown_records": unknown, "inventory": inventory, "followups": followups}


__all__ = ["minimize", "run_ref"]
