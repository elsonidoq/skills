#!/usr/bin/env python3
"""Opt-in READ-ONLY RPC scenario recorder. Completion is not semantic acceptance."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

DIALOGS = {"select", "input", "editor", "confirm"}


def answer_dialog(request, step):
    if request.get("method") != step["method"]:
        raise ValueError("unexpected dialog method")
    if step.get("title_contains", "") not in request.get("title", ""):
        raise ValueError("unexpected dialog title")
    payload = step["response"]
    if request["method"] == "select" and not payload.get("cancelled"):
        if payload.get("value") not in request.get("options", []):
            raise ValueError("scripted option was not actually offered")
    if request["method"] == "confirm" and not payload.get("cancelled"):
        if not isinstance(payload.get("confirmed"), bool):
            raise ValueError("confirm response requires a boolean")
    if request["method"] in {"input", "editor"} and not payload.get("cancelled"):
        if not isinstance(payload.get("value"), str):
            raise ValueError("text response requires a string")
    return {**payload, "type": "extension_ui_response", "id": request["id"]}


def record(command, prompt, dialogs, output, cwd, env=None, timeout=120, max_events=5000):
    """LF-framed binary reader; stdout must keep draining while UI blocks.

    This function also supports a fake RPC process for offline driver tests. CLI uses
    only pi's pinned documented interface; no arbitrary command option is exposed.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    records = queue.Queue()
    failure, count, answers = None, 0, 0
    with (output / "stderr.log").open("xb") as stderr, (output / "events.jsonl").open("x") as log:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=stderr, start_new_session=True)
        def drain():
            try:
                while line := proc.stdout.readline():
                    records.put(line)
            finally:
                records.put(None)
        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        def send(value):
            proc.stdin.write(json.dumps(value).encode() + b"\n")
            proc.stdin.flush()
        try:
            send({"id": "scenario", "type": "prompt", "message": prompt})
            deadline = time.monotonic() + timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("scenario deadline elapsed")
                line = records.get(timeout=remaining)
                if line is None:
                    raise RuntimeError("RPC process exited before agent_settled")
                event = json.loads(line)
                log.write(json.dumps(event) + "\n"); log.flush()
                count += 1
                if count > max_events:
                    raise RuntimeError("event budget exceeded")
                if event.get("type") == "response" and not event.get("success"):
                    raise RuntimeError(f"RPC command failed: {event.get('error')}")
                if event.get("type") == "extension_error":
                    raise RuntimeError(f"extension failed: {event.get('error')}")
                if event.get("type") == "message_end":
                    message = event.get("message", {})
                    if message.get("role") == "assistant" and message.get("stopReason") in {"error", "aborted"}:
                        raise RuntimeError("model response failed or aborted")
                if event.get("type") == "tool_execution_end" and event.get("isError"):
                    raise RuntimeError("tool failed; inspect trace before retry")
                if event.get("type") == "tool_execution_start":
                    if event.get("toolName") not in {"read", "grep", "find", "ls", "ask_user"}:
                        raise RuntimeError("tool outside read-only smoke profile attempted")
                if event.get("type") == "extension_ui_request" and event.get("method") in DIALOGS:
                    if answers >= len(dialogs):
                        raise RuntimeError("unscripted owner question; refusing inferred answer")
                    response = answer_dialog(event, dialogs[answers])
                    send(response)
                    log.write(json.dumps({"type": "harness_ui_response", "response": response}) + "\n")
                    log.flush(); answers += 1
                if event.get("type") == "agent_settled":
                    if answers != len(dialogs):
                        raise RuntimeError("agent stopped before expected owner dialogs")
                    break
        except Exception as exc:
            failure = str(exc) or type(exc).__name__
        finally:
            try:
                proc.stdin.close()
                proc.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                # Stop the entire read-only process group, not just a stranded parent.
                import signal
                import contextlib
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            reader.join(timeout=2)
            proc.stdout.close()
        if proc.returncode and failure is None:
            failure = f"RPC process exit {proc.returncode}"
    result = {"driver": "FAIL" if failure else "COMPLETED", "error": failure,
              "dialogs_answered": answers, "events": count,
              "acceptance": "NOT EVALUATED: trace assertions and independent semantic review required"}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("scenario", type=Path, help="JSON prompt and exact scripted RPC dialogs")
    p.add_argument("--authorize-live", action="store_true", help="explicitly authorize model invocation")
    p.add_argument("--model", required=True, help="owner-selected exact provider/model")
    p.add_argument("--ask-extension", type=Path, required=True, help="verified pinned extension entry")
    p.add_argument("--agent-dir", type=Path, required=True, help="isolated, owner-prepared runtime/auth configuration")
    p.add_argument("--cwd", type=Path, required=True, help="disposable fixture with .planner-test-sandbox marker")
    p.add_argument("--output", type=Path, required=True, help="new evidence directory")
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    if not args.authorize_live:
        p.error("live runs require explicit --authorize-live and prior owner authorization")
    if not (args.cwd / ".planner-test-sandbox").is_file():
        p.error("disposable fixture marker missing")
    if not args.ask_extension.exists() or not args.agent_dir.is_dir() or args.timeout <= 0:
        p.error("verified extension, isolated runtime directory and positive timeout required")
    suite = Path(__file__).resolve().parents[1]
    scenario = json.loads(args.scenario.read_text())
    command = ["pi", "--mode", "rpc", "--no-session", "--offline", "--no-extensions",
               "--no-skills", "--no-prompt-templates", "--no-themes", "--model", args.model,
               "--extension", str(args.ask_extension.resolve()), "--skill", str(suite / "skills"),
               "--tools", "read,grep,find,ls,ask_user"]
    env = dict(os.environ, PI_CODING_AGENT_DIR=str(args.agent_dir.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Save reproducibility metadata with the collector result, not credentials.
    result = record(command, scenario["prompt"], scenario["dialogs"], args.output,
                    args.cwd, env, args.timeout)
    import hashlib
    identity = {"model": args.model, "command": command, "profile": "read-only smoke",
                "skills": {str(f.relative_to(suite)): hashlib.sha256(f.read_bytes()).hexdigest()
                           for f in sorted((suite / "skills").rglob("SKILL.md"))}}
    (args.output / "identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["driver"] != "COMPLETED"


if __name__ == "__main__":
    raise SystemExit(main())
