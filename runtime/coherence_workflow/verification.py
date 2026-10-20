"""Run actual optional project commands; no registered check/evidence catalogue."""
import subprocess

from .store import Blocked


def commands(task):
    values = list(task.get('checks', []))
    for item in task.get('required', []):
        if 'check' in item:
            values.append(item['check'])
    if 'check' in task:
        values.append(task['check'])
    return values


def run_checks(project, task):
    results = []
    for value in commands(task):
        command = value.get('command', value.get('argv')) if isinstance(value, dict) else value
        if not isinstance(command, (str, list)) or not command or (isinstance(command, list) and
                any(not isinstance(arg, str) for arg in command)):
            raise Blocked('task ' + task['id'] + ' check needs a command string or argv list; registered check IDs are no longer executable')
        # No workflow deadline or output cap. Preserve normal shell/project behavior.
        result = subprocess.run(command, cwd=project, shell=isinstance(command, str))
        results.append({'command': command, 'exit_code': result.returncode})
        if result.returncode:
            raise Blocked('task ' + task['id'] + ' check failed (exit ' + str(result.returncode) + '): ' + str(command))
    return results


def manual_gates(task, question):
    for gate in task.get('gates', []):
        text = gate if isinstance(gate, str) else gate.get('question', gate.get('description'))
        if not isinstance(text, str):
            raise Blocked('manual gate needs a question or description for task ' + task['id'])
        answer = question(text + '\nApprove this gate? [yes/no]')
        if answer.strip().lower() not in ('yes', 'y'):
            raise Blocked('manual gate not approved for task ' + task['id'])
