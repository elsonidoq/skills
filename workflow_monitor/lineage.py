"""Resolve only explicitly declared local correction relationships."""
from __future__ import annotations

from typing import Any


def resolve(runs: list[dict[str, Any]], occurrences: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Return declared followups and conservative review-coverage summaries.

    A declaration is useful only when it names a recorded reviewer occurrence in this
    fixed reader snapshot.  This intentionally does not consult Git ancestry, names,
    timestamps, or any other worktree.
    """
    by_run = {row["run_id"]: row for row in runs}
    reviews: dict[tuple[str, str], dict[str, Any]] = {}
    current_heads: dict[str, str | None] = {run_id: None for run_id in by_run}
    for occurrence in occurrences:
        run_id = occurrence["run_id"]
        for observation in occurrence["observations"]:
            facts = observation["facts"]
            if observation["phase"] == "checkpoint" and isinstance(facts.get("head"), str):
                current_heads[run_id] = facts["head"]
        first = occurrence["observations"][0] if occurrence["observations"] else {}
        facts = first.get("facts", {})
        if occurrence["phase"] == "review" and facts.get("role") == "reviewer":
            terminal = next((item for item in reversed(occurrence["observations"])
                             if item["kind"] in {"passed", "failed", "interrupted"}), None)
            if terminal:
                reviews[(run_id, occurrence["occurrence_id"])] = {"run_id": run_id, "occurrence_id": occurrence["occurrence_id"],
                    "base": terminal["facts"].get("review_base"), "head": terminal["facts"].get("review_head"),
                    "approved": terminal["facts"].get("approved") is True and terminal["facts"].get("finding_count") == 0,
                    "complete": terminal["kind"] in {"passed", "failed"}}
                if isinstance(terminal["facts"].get("review_head"), str):
                    current_heads[run_id] = terminal["facts"]["review_head"]

    followups: list[dict[str, Any]] = []
    parent: dict[str, str] = {}
    for run_id, run in by_run.items():
        correction = (run.get("description") or {}).get("correction_of")
        if not (isinstance(correction, dict) and isinstance(correction.get("run_id"), str) and
                isinstance(correction.get("review_execution_id"), str)):
            continue
        source_run, review_id = correction["run_id"], correction["review_execution_id"]
        resolved = (source_run, review_id) in reviews
        relation = {"run_id": run_id, "source_run_id": source_run, "review_occurrence_id": review_id,
                    "resolution": "resolved" if resolved else "unresolved"}
        followups.append(relation)
        if resolved:
            parent[run_id] = source_run

    # Multiple successors claiming the same reviewer reference cannot be ordered or
    # authorized by the declaration alone.
    references: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for relation in followups:
        if relation["resolution"] == "resolved":
            references.setdefault((relation["source_run_id"], relation["review_occurrence_id"]), []).append(relation)
    for duplicates in references.values():
        if len(duplicates) > 1:
            for relation in duplicates:
                relation["resolution"] = "conflicting"
                parent.pop(relation["run_id"], None)

    # A valid-looking reference which closes a declared relationship is still unknown.
    for relation in followups:
        if relation["resolution"] != "resolved":
            continue
        seen: set[str] = set()
        node = relation["run_id"]
        while node in parent:
            if node in seen:
                relation["resolution"] = "cyclic"
                for candidate in followups:
                    if candidate["run_id"] in seen:
                        candidate["resolution"] = "cyclic"
                break
            seen.add(node)
            node = parent[node]

    def completed_repair(run_id: str) -> bool:
        """Require the recorded fixing worker, check, and checkpoint boundaries."""
        run_occurrences = [item for item in occurrences if item["run_id"] == run_id]
        def has(phase: str, predicate) -> bool:
            return any(item["phase"] == phase and predicate(item["observations"]) for item in run_occurrences)
        return (has("worker", lambda rows: rows and rows[0]["facts"].get("role") == "fixing_worker" and
                    any(row["kind"] == "returned" for row in rows)) and
                has("check", lambda rows: any(row["kind"] == "passed" for row in rows)) and
                has("checkpoint", lambda rows: any(row["kind"] == "passed" for row in rows)))

    summaries: dict[str, dict[str, Any]] = {}
    for run_id in by_run:
        summaries[run_id] = {"state": "unknown", "base": None, "head": current_heads[run_id]}
    for relation in followups:
        if relation["resolution"] != "resolved":
            continue
        original = reviews[(relation["source_run_id"], relation["review_occurrence_id"])]
        leaf = relation["run_id"]
        # A newer linked correction changes the displayed current head; an older review
        # cannot be presented as current acceptance.
        while True:
            children = [item["run_id"] for item in followups if item["source_run_id"] == leaf and item["resolution"] == "resolved"]
            if not children:
                break
            leaf = children[-1]
        candidates = [value for key, value in reviews.items() if key[0] == leaf]
        latest = candidates[-1] if candidates else None
        head = current_heads[leaf]
        chain: list[str] = []
        node = leaf
        while node != relation["source_run_id"]:
            chain.append(node)
            node = parent[node]
        repairs_complete = all(completed_repair(run_id) for run_id in chain)
        if latest is None or not latest["complete"]:
            state = "unknown"
        elif latest["approved"] and latest["base"] == original["base"] and latest["head"] == head:
            state = "accepted_full_range" if repairs_complete and not original["approved"] else "unknown"
        elif latest["approved"]:
            state = "correction_only"
        else:
            state = "not_accepted"
        summaries[relation["source_run_id"]] = {"state": state, "base": original["base"], "head": head}
        summaries[leaf] = {"state": state, "base": original["base"], "head": head}
    return followups, summaries


__all__ = ["resolve"]
