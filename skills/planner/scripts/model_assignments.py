"""Resolve the planner's installed owner-editable assignment file."""
import json
from pathlib import Path


class AssignmentError(ValueError):
    """An owner-editable assignment cannot resolve for one planning operation."""


def assignment_path(planner_skill=None):
    """Find the JSON beside the installed planner skill, following its symlink."""
    anchor = Path(planner_skill) if planner_skill is not None else Path(__file__)
    anchor = anchor.resolve()
    root = anchor.parent if anchor.is_file() else anchor
    if root.name == "scripts":
        root = root.parent
    return root / "references" / "model-assignments.json"


def _problem(operation, path, problem):
    return AssignmentError(
        f"Planning operation {operation!r} cannot resolve in {path}: {problem}. "
        f"Ask the owner to correct the assignment for {operation!r}."
    )


def _load(path, operation):
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise _problem(operation, path, "assignment file is absent") from None
    except json.JSONDecodeError as exc:
        raise _problem(operation, path, f"assignment JSON is malformed ({exc.msg})") from None
    if not isinstance(data, dict):
        raise _problem(operation, path, "assignment JSON must be an object")
    return data


def _binding(operation, path, value):
    if not isinstance(value, dict):
        raise _problem(operation, path, "assignment must be an object")
    model, effort = value.get("model"), value.get("effort")
    if not isinstance(model, str) or not model or not isinstance(effort, str) or not effort:
        raise _problem(operation, path, "assignment needs nonempty model and effort")
    return {"model": model, "effort": effort}


def resolve(operation, *, launched_parent=None, planner_skill=None):
    """Return the requested binding for an operation from the actual installed JSON."""
    path = assignment_path(planner_skill)
    data = _load(path, operation)
    operations, assignments = data.get("operations"), data.get("assignments")
    if not isinstance(operations, dict) or not isinstance(assignments, dict):
        raise _problem(operation, path, "operations and assignments must be objects")
    entry = operations.get(operation)
    if entry is None:
        raise _problem(operation, path, "operation has no assignment")
    if not isinstance(entry, dict):
        raise _problem(operation, path, "operation assignment must be an object")
    has_inheritance, has_assignment = "inherit" in entry, "assignment" in entry
    if has_inheritance == has_assignment:
        raise _problem(operation, path, "operation must contain exactly one of inherit or assignment")
    if has_inheritance:
        if entry["inherit"] != "launched-parent":
            raise _problem(operation, path, "inheritance must be launched-parent")
        if launched_parent is None:
            raise _problem(operation, path, "launched-parent model and effort are required")
        binding = _binding(operation, path, launched_parent)
        source = "launched-parent"
    else:
        name = entry["assignment"]
        if not isinstance(name, str) or not name:
            raise _problem(operation, path, "saved assignment name must be a nonempty string")
        if name not in assignments:
            raise _problem(operation, path, f"saved assignment {name!r} is absent")
        binding = _binding(operation, path, assignments[name])
        source = name
    return {"operation": operation, "requested": binding, "source": source, "path": str(path)}


def resolve_correction(producing_operation, **kwargs):
    """Corrections reuse their producing stage; there is no repair assignment."""
    return resolve(producing_operation, **kwargs)
