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
               "no_change", "review_base", "review_head", "approved", "outcome", "finding_count", "execution_id",
               "review_ordinal", "trigger_execution_id", "predecessor_execution_id", "recording_gap", "invocation_id",
               "invocation_kind", "selected_input_checkpoints", "correction_chain", "predecessor_invocation_id",
               "stopped_by_invocation_id", "support_invocation_id", "producer_invocation_id", "fixing_round"}
    if set(facts) - allowed:
        return False
    return (not isinstance(facts.get("role"), (list, dict)) and
            ("ordinal" not in facts or type(facts["ordinal"]) is int) and
            ("exit_code" not in facts or type(facts["exit_code"]) is int) and
            ("finding_count" not in facts or type(facts["finding_count"]) is int) and
            ("review_ordinal" not in facts or type(facts["review_ordinal"]) is int) and
            ("fixing_round" not in facts or type(facts["fixing_round"]) is int) and
            ("execution_id" not in facts or isinstance(facts["execution_id"], str)) and
            ("trigger_execution_id" not in facts or isinstance(facts["trigger_execution_id"], str)) and
            ("predecessor_execution_id" not in facts or isinstance(facts["predecessor_execution_id"], str)) and
            all(isinstance(facts[key], str) and facts[key] for key in {"invocation_id", "invocation_kind", "predecessor_invocation_id", "stopped_by_invocation_id", "support_invocation_id", "producer_invocation_id"} & set(facts)) and
            ("invocation_kind" not in facts or facts["invocation_kind"] in {"task_worker", "corrective_worker"}) and
            ("selected_input_checkpoints" not in facts or isinstance(facts["selected_input_checkpoints"], list)) and
            ("correction_chain" not in facts or isinstance(facts["correction_chain"], list)) and
            ("outcome" not in facts or facts["outcome"] in {"approved", "rejected", "failed", "interrupted"}) and
            ("no_change" not in facts or type(facts["no_change"]) is bool) and
            ("approved" not in facts or type(facts["approved"]) is bool))


def _descriptor(row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return only a complete, closed declared plan; never repair a partial one."""
    description = _object(row.get("description"))
    if description is None or description.get("version") != 1 or description.get("description_version") != 3:
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
            len(set(task_ids)) != len(task_ids) or
            any(set(task) != {"id", "depends", "label", "work_description"} or
                not isinstance(task.get("label"), str) or not task["label"] or
                (task.get("work_description") is not None and not isinstance(task.get("work_description"), str))
                for task in tasks)):
        return None, "description_invalid"
    dependencies = {task["id"]: task.get("depends") for task in tasks}
    if any(not isinstance(values, list) or any(not isinstance(value, str) or value not in dependencies or value == task_id
                                                for value in values) or len(set(values)) != len(values)
           for task_id, values in dependencies.items()):
        return None, "description_invalid"
    initial_review = description.get("initial_review")
    if initial_review is not None and initial_review != {"planned": True}:
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
            tasks.append({"run_id": run_id, "task_id": task_id, "label": task.get("label"),
                          "work_description": task.get("work_description"), "depends": task.get("depends")})
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
    # The review-chain table supplies safe details, but an execution exists publicly only
    # when its matching monitoring occurrence was actually recorded.
    execution_occurrences: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        execution_id = observation["facts"].get("execution_id")
        if isinstance(execution_id, str) and execution_id:
            execution_occurrences[(observation["run_id"], execution_id)].append(observation)
    chain_by_execution: dict[tuple[str, str], dict[str, Any]] = {}
    for detail in snapshot.get("review_details", []):
        if not isinstance(detail, dict):
            continue
        run_id, execution_id = detail.get("run_id"), detail.get("execution_id")
        rows = execution_occurrences.get((run_id, execution_id), [])
        if not isinstance(run_id, str) or not isinstance(execution_id, str):
            continue
        attempt = {key: detail.get(key) for key in ("attempt_seq", "outcome", "uncertain", "findings", "commit_refs")}
        current = chain_by_execution.get((run_id, execution_id))
        if current is None:
            # A persisted reviewer execution is exact dispatch evidence even when
            # optional observation recording failed.  A fixer execution remains a
            # round notice below; it is not an individual model invocation.
            chain_by_execution[(run_id, execution_id)] = {**detail, "attempts": [attempt],
                                                           "occurrence_ids": sorted({row["occurrence_id"] for row in rows})}
        else:
            current["attempts"].append(attempt)
            # Reader order is the append-only attempt sequence, so later is the current
            # outcome while the earlier authorized diagnostic/review history remains.
            current.update({key: value for key, value in detail.items() if key != "attempt_seq"})
    all_chain = list(chain_by_execution.values())
    # Review executions identify reviewer calls.  Fixer executions identify only
    # the assigned round: its individual calls come exclusively from exact
    # fixer_invocation history or recorded invocation IDs.
    fixing_rounds = [item for item in all_chain if item.get("role") == "fixer"]
    chain = [item for item in all_chain if item.get("role") == "reviewer"]
    known_executions = {(row["run_id"], row["execution_id"]) for row in chain}
    for item in chain:
        run_id, execution_id = item["run_id"], item["execution_id"]
        for relation in ("trigger_execution_id", "predecessor_execution_id"):
            target = item.get(relation)
            if isinstance(target, str) and (run_id, target) in known_executions:
                edges.append({"run_id": run_id, "type": "chain_" + relation.removesuffix("_execution_id"),
                              "from": ("execution", target), "to": ("execution", execution_id)})
    for observation in observations:
        execution_id = observation["facts"].get("execution_id")
        if (observation["run_id"], execution_id) not in known_executions:
            continue
        if observation["phase"] in {"check", "checkpoint"}:
            edges.append({"run_id": observation["run_id"], "type": "chain_" + observation["phase"],
                          "from": ("execution", execution_id), "to": ("observation", observation["seq"])})
    chain_acceptance = {}
    for run_id in known_runs:
        candidates = [item for item in chain if item["run_id"] == run_id and item.get("role") == "reviewer"]
        terminal = max(candidates, key=lambda item: item.get("review_ordinal") or 0, default=None)
        if terminal and terminal.get("outcome") == "approved" and not terminal.get("findings") and not terminal.get("uncertain"):
            chain_acceptance[run_id] = {"state": "accepted", "execution_id": terminal["execution_id"],
                                        "base": terminal.get("review_base"), "head": terminal.get("review_head")}
        else:
            chain_acceptance[run_id] = {"state": "unknown", "execution_id": None, "base": None, "head": None}
    followups, review_acceptance = resolve(runs, occurrences)
    # Closed actual-call readback: relationships are preserved only where the producer
    # recorded exact invocation/checkpoint identities.  This deliberately does not
    # turn occurrence ordering, task dependencies, or review table adjacency into input.
    activities: list[dict[str, Any]] = []
    by_invocation: dict[tuple[str, str], dict[str, Any]] = {}
    for occurrence in occurrences:
        rows = occurrence["observations"]
        facts = rows[0]["facts"] if rows else {}
        def call_identity(value):
            return value.get('invocation_id') or (value.get('execution_id') if value.get('role') == 'reviewer' else None)
        invocation_id = call_identity(facts)
        if not isinstance(invocation_id, str) or not invocation_id:
            continue
        if any(call_identity(row['facts']) != invocation_id for row in rows):
            unknown.append({"run_id": occurrence["run_id"], "seq": rows[0]["seq"], "code": "unsupported_observation"})
            continue
        terminal = next((row for row in reversed(rows) if row['kind'] in {'returned', 'failed', 'interrupted'} or (facts.get('role') == 'reviewer' and row['kind'] == 'passed')), None)
        activity = {"run_id": occurrence["run_id"], "invocation_id": invocation_id,
                    "occurrence_id": occurrence["occurrence_id"], "task_id": occurrence["task_id"],
                    "role": facts.get("role"), "invocation_kind": facts.get("invocation_kind"),
                    "selected_input_checkpoints": facts.get("selected_input_checkpoints"),
                    "correction_chain": facts.get("correction_chain") or [],
                    "predecessor_invocation_id": facts.get("predecessor_invocation_id"),
                    "trigger_execution_id": facts.get("trigger_execution_id"),
                    "outcome": ('returned' if terminal['kind'] == 'passed' else terminal['kind']) if terminal else 'unknown',
                    "error_category": terminal["facts"].get("error_category") if terminal else None,
                    "support_invocation_id": terminal["facts"].get("support_invocation_id") if terminal else None,
                    "stopped_by_invocation_id": terminal["facts"].get("stopped_by_invocation_id") if terminal else None,
                    "record_refs": [row["seq"] for row in rows]}
        if (occurrence["run_id"], invocation_id) in by_invocation:
            unknown.append({"run_id": occurrence["run_id"], "seq": rows[0]["seq"], "code": "unsupported_observation"})
            continue
        by_invocation[(occurrence["run_id"], invocation_id)] = activity
        activities.append(activity)
    # Dispatch history can prove a scheduled worker/reviewer call even when the
    # optional observation row is absent.  It never supplies a call for a fixer
    # round; only a retained fixer_invocation identity does that.
    dispatches = snapshot.get("dispatches") if isinstance(snapshot.get("dispatches"), dict) else {}
    round_by_execution = {(item["run_id"], item["execution_id"]): item for item in fixing_rounds}
    for run_id, calls in dispatches.items():
        if not isinstance(run_id, str) or not isinstance(calls, list):
            continue
        for call in calls:
            if not isinstance(call, dict):
                continue
            invocation_id, role = call.get("invocation_id"), call.get("role")
            if not isinstance(invocation_id, str) or not invocation_id or role not in {"worker", "fixing_worker", "reviewer"}:
                continue
            key = (run_id, invocation_id)
            if key in by_invocation:
                continue
            execution_id = call.get("execution_id") if isinstance(call.get("execution_id"), str) else None
            fixing_round = round_by_execution.get((run_id, execution_id))
            activity = {"run_id": run_id, "invocation_id": invocation_id, "occurrence_id": None,
                        "task_id": call.get("task_id") if isinstance(call.get("task_id"), str) else None,
                        "role": role, "invocation_kind": None, "selected_input_checkpoints": None,
                        "correction_chain": [], "predecessor_invocation_id": None,
                        "trigger_execution_id": (call.get("trigger_execution_id") if isinstance(call.get("trigger_execution_id"), str)
                                                 else fixing_round.get("trigger_execution_id") if fixing_round else None),
                        "outcome": "unknown", "error_category": None, "support_invocation_id": None,
                        "stopped_by_invocation_id": None, "record_refs": [], "dispatch_observed": False}
            by_invocation[key] = activity
            activities.append(activity)
    metric_sets = snapshot.get("metrics") if isinstance(snapshot.get("metrics"), dict) else {}
    for activity in activities:
        metric_set = metric_sets.get(activity["run_id"])
        if isinstance(metric_set, dict):
            records = metric_set.get("records") if isinstance(metric_set.get("records"), list) else []
            matches = [record for record in records if isinstance(record, dict) and record.get("invocation_id") == activity["invocation_id"]]
            def matching_metric(record):
                if not isinstance(record, dict) or record.get("invocation_id") != activity["invocation_id"]:
                    return False
                if record.get("task_id") != activity["task_id"]:
                    return False
                dispatches = [call for call in metric_set.get('dispatches', []) if call.get('invocation_id') == activity['invocation_id']]
                if any(call.get('task_id') != activity['task_id'] or call.get('role') != activity['role'] for call in dispatches):
                    return False
                role = ('corrective_worker' if activity['role'] == 'worker' and activity['invocation_kind'] == 'corrective_worker' else activity['role'])
                roles = {'worker': {'worker'}, 'corrective_worker': {'corrective_worker'},
                         'fixing_worker': {'fixing_worker'}, 'reviewer': {'reviewer'}}
                return record.get('role') in roles.get(role, set())
            matches = [record for record in records if matching_metric(record)]
            activity["metric"] = matches[0] if len(matches) == 1 else None
            activity["metric_coverage"] = metric_set.get("coverage") if metric_set.get("coverage") in {"complete", "partial", "unavailable"} else "unavailable"
            activity["metric_reasons"] = [reason for reason in metric_set.get("reasons", []) if isinstance(reason, str)]
            if any(record.get('invocation_id') == activity['invocation_id'] for record in records) and len(matches) != 1:
                activity['metric_reasons'].append('metric_association_mismatch')
                activity['metric_coverage'] = 'partial'
        else:
            activity["metric"] = None
            activity["metric_coverage"] = "unavailable"
            activity["metric_reasons"] = ["metric_artifact_unavailable"]
        inputs = activity["selected_input_checkpoints"]
        if not isinstance(inputs, list):
            activity["input_qualification"] = "unknown"
            continue
        references = []
        valid = True
        for item in inputs:
            if not isinstance(item, dict) or set(item) != {"checkpoint_occurrence_id", "task_id", "producer_invocation_id", "correction_chain"}:
                valid = False; break
            producer = item.get("producer_invocation_id")
            if not isinstance(producer, str) or (activity["run_id"], producer) not in by_invocation:
                valid = False; break
            references.append(producer)
        activity["input_invocation_ids"] = references if valid else []
        activity["input_qualification"] = "recorded" if valid else "unknown"
    def aggregate(records, expected_ids, coverage):
        import math
        fields = {}
        for name in ('input', 'output', 'cache_read', 'cache_write', 'total_tokens', 'estimated_usd'):
            values = []
            for record in records:
                interval = record.get('interval', {})
                field = interval.get('tokens', {}).get(name) if name in {'input', 'output', 'cache_read', 'cache_write'} else interval.get(name)
                number = field.get('value') if isinstance(field, dict) else None
                if type(number) in (int, float) and math.isfinite(number) and number >= 0:
                    values.append(number)
            complete = coverage == 'complete' and bool(expected_ids) and {row['invocation_id'] for row in records} == expected_ids and len(values) == len(records)
            fields[name] = {'known_subtotal': sum(values) if values else None,
                            'full_total': sum(values) if complete else None,
                            'known_interval_count': len(values)}
        return {'fields': fields, 'interval_count': len(records), 'dispatch_count': len(expected_ids),
                'distinct_membership_count': len({row['task_id'] for row in records if row.get('task_id') is not None})}

    aggregates = {}
    for run_id, metric_set in metric_sets.items():
        if not isinstance(metric_set, dict):
            continue
        dispatch = {row['invocation_id']: row for row in metric_set.get('dispatches', [])}
        records = []
        for record in metric_set.get('records', []):
            call = dispatch.get(record.get('invocation_id'))
            activity = by_invocation.get((run_id, record.get('invocation_id')))
            # An observed call must agree exactly; surviving dispatch history can
            # supply attribution when optional observation recording was lost.
            dispatch_matches = call is not None and call['task_id'] == record.get('task_id') and record.get('role') in ({'worker', 'corrective_worker'} if call['role'] == 'worker' else {call['role']})
            if activity is not None:
                valid = activity.get('metric') == record and (call is None or dispatch_matches)
            else:
                valid = dispatch_matches
            if valid:
                records.append(record)
        coverage = metric_set.get('coverage')
        if len(records) != len(metric_set.get('records', [])):
            coverage = 'partial'
            metric_set['coverage'] = coverage
            metric_set['reasons'] = sorted(set(metric_set.get('reasons', []) + ['unattributed_intervals']))
        task_ids = {row['task_id'] for row in dispatch.values() if row['task_id'] is not None}
        aggregates[run_id] = {
            'tasks': {task_id: aggregate([row for row in records if row.get('task_id') == task_id],
                        {identity for identity, row in dispatch.items() if row['task_id'] == task_id}, coverage) for task_id in task_ids},
            **{scope: aggregate([row for row in records if (row['role'] == 'reviewer') == reviewer],
                {identity for identity, row in dispatch.items() if (row['role'] == 'reviewer') == reviewer}, coverage)
               for scope, reviewer in [('worker_fixer', False), ('reviewer', True)]}}
    for activity in activities:
        activity['task_metrics'] = aggregates.get(activity['run_id'], {}).get('tasks', {}).get(activity['task_id'])
    # First-review input membership is a recorded producer relationship, not a
    # plan/dependency inference.  It is projected only when every checkpoint
    # names an exact known invocation in this run.
    for execution in chain:
        inputs = execution.get("input_checkpoints")
        producers = []
        if isinstance(inputs, list):
            for item in inputs:
                producer = item.get("producer_invocation_id") if isinstance(item, dict) else None
                if not isinstance(producer, str) or (execution["run_id"], producer) not in by_invocation:
                    producers = []; break
                producers.append(producer)
        execution["input_invocation_ids"] = producers
    return {"state": "ok", "runs": runs, "phases": phases, "tasks": tasks, "occurrences": occurrences,
            "observations": observations, "edges": edges, "unknown_records": unknown,
            "unsupported_run_ids": list(snapshot.get("unsupported_run_ids", [])), "followups": followups,
            "review_acceptance": review_acceptance, "chain": chain, "fixing_rounds": fixing_rounds,
            "chain_acceptance": chain_acceptance, "activities": activities, "metric_aggregates": aggregates,
            "metric_artifacts": snapshot.get('metric_artifacts', {}),
            "metrics": {run_id: {"coverage": value.get("coverage"), "reasons": value.get("reasons", []),
                                   "interval_count": len(value.get("records", [])) if isinstance(value.get("records"), list) else 0,
                                   "distinct_membership_count": len({row.get("task_id") for row in value.get("records", []) if isinstance(row, dict) and isinstance(row.get("task_id"), str)}),
                                   "worker_fixer_records": sum(1 for row in value.get("records", []) if isinstance(row, dict) and row.get("role") != "reviewer"),
                                   "reviewer_records": sum(1 for row in value.get("records", []) if isinstance(row, dict) and row.get("role") == "reviewer")}
                        for run_id, value in metric_sets.items() if isinstance(run_id, str) and isinstance(value, dict)}}


__all__ = ["normalize"]
