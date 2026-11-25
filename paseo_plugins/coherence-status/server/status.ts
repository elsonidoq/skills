import { existsSync } from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import type { WorkflowStatus } from "../shared/status";

const DATABASE = path.join(".coherence", "workflow", "workflow.sqlite");

// One workflow runs per worktree at a time, so show the running run, else the run
// with the most recent history entry.
const RUN_QUERY = `
  SELECT r.run_id AS runId, r.state AS state
  FROM execution_runs r
  LEFT JOIN (SELECT run_id, MAX(recorded_at) AS last FROM execution_history GROUP BY run_id) h
    ON h.run_id = r.run_id
  ORDER BY (r.state = 'running') DESC, h.last DESC, r.rowid DESC
  LIMIT 1`;

const TASKS_QUERY = `
  SELECT t.task_id AS taskId, t.state AS state,
    (SELECT MAX(recorded_at) FROM execution_history h
      WHERE h.run_id = t.run_id AND h.task_id = t.task_id
        AND h.kind = 'task' AND h.state = 'running') AS startedAt
  FROM execution_tasks t
  WHERE t.run_id = ?
  ORDER BY t.rowid`;

type TaskRow = { taskId: string; state: string; startedAt: number | null };

// A task row exists only after the task starts; the run contract lists every task.
function contractTaskIds(db: DatabaseSync, runId: string): string[] {
  const table = db.prepare("SELECT 1 FROM sqlite_master WHERE name = 'execution_run_inputs'").get();
  if (!table) return [];
  const row = db.prepare("SELECT contract FROM execution_run_inputs WHERE run_id = ?").get(runId) as
    | { contract: string }
    | undefined;
  if (!row) return [];
  const tasks = (JSON.parse(row.contract) as { tasks?: { id?: unknown }[] }).tasks ?? [];
  return tasks.map((task) => task.id).filter((id): id is string => typeof id === "string");
}

export function readWorkflowStatus(directory: string): WorkflowStatus {
  const file = path.join(directory, DATABASE);
  if (!existsSync(file)) {
    return { run: null, tasks: [], message: `No Coherence workflow in ${directory}.` };
  }
  const db = new DatabaseSync(file, { readOnly: true });
  try {
    const run = db.prepare(RUN_QUERY).get() as { runId: string; state: string } | undefined;
    if (!run) {
      return { run: null, tasks: [], message: "The workflow database has no runs." };
    }
    const rows = db.prepare(TASKS_QUERY).all(run.runId) as TaskRow[];
    const started = new Map(rows.map((row) => [row.taskId, row]));
    const ordered = contractTaskIds(db, run.runId).map(
      (taskId) => started.get(taskId) ?? { taskId, state: "pending", startedAt: null },
    );
    const listed = new Set(ordered.map((row) => row.taskId));
    ordered.push(...rows.filter((row) => !listed.has(row.taskId)));
    return {
      run: { runId: run.runId, state: run.state },
      tasks: ordered.map((row) => ({
        taskId: row.taskId,
        state: row.state,
        startedAt: row.startedAt === null ? null : Math.round(row.startedAt * 1000),
      })),
      message: null,
    };
  } finally {
    db.close();
  }
}
