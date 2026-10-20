"""Task-file parsing and the six executable intake checks."""
import copy
import hashlib
import json
from pathlib import Path

import yaml

from .store import Blocked


def content_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def admit(contract):
    """Validate work and sort dependencies; optional task context stays intact."""
    result = {'tasks': copy.deepcopy(contract)} if isinstance(contract, list) else copy.deepcopy(contract)
    if not isinstance(result, dict) or not isinstance(result.get('tasks'), list):
        raise Blocked('task input must contain a task list; supply a list or an object with tasks')
    tasks = result['tasks']
    by_id = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get('id'), str) or not task['id'].strip():
            raise Blocked('each task needs a nonempty string id')
        description = task.get('outcome', task.get('description'))
        if not isinstance(description, str) or not description.strip():
            raise Blocked('task '+task['id']+' needs a work description (outcome or description)')
        if task['id'] in by_id:
            raise Blocked('duplicate task id: '+task['id'])
        by_id[task['id']] = task
        dependencies = task.get('depends', [])
        if not isinstance(dependencies, list) or any(not isinstance(dep, str) for dep in dependencies):
            raise Blocked('task '+task['id']+' depends must be a list of task IDs')
    for task in tasks:
        for dep in task.get('depends', []):
            if dep not in by_id:
                raise Blocked('task '+task['id']+' references missing dependency: '+dep)
    # Iterative topological ordering also handles long, ordinary task lists.
    remaining = {key: set(task.get('depends', [])) for key, task in by_id.items()}
    consumers = {key: [] for key in by_id}
    for key, deps in remaining.items():
        for dep in deps:
            consumers[dep].append(key)
    ready = [key for key in by_id if not remaining[key]]
    ordered = []
    for key in ready:
        ordered.append(by_id[key])
        for consumer in consumers[key]:
            remaining[consumer].discard(key)
            if not remaining[consumer]:
                ready.append(consumer)
    if len(ordered) != len(tasks):
        raise Blocked('dependency cycle involving: '+', '.join(key for key, deps in remaining.items() if deps))
    result['tasks'] = ordered
    return result


def load_contract(path):
    path = Path(path)
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        raise Blocked(f'cannot read task input {path}: {exc}; supply a readable JSON/YAML file') from None
    try:
        value = json.loads(text) if path.suffix.lower() == '.json' else yaml.safe_load(text)
    except (ValueError, yaml.YAMLError) as exc:
        raise Blocked(f'cannot parse task input {path}: {exc}') from None
    return admit(value)
