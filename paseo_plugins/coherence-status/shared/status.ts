import { defineRpc } from "@getpaseo/plugin";
import { z } from "zod";

export const taskSchema = z.object({
  taskId: z.string(),
  state: z.string(),
  // Epoch milliseconds of the latest time the task entered "running"; null if it never ran.
  startedAt: z.number().nullable(),
});

export const workflowStatus = defineRpc({
  name: "coherence-status.read",
  input: z.object({ workspaceId: z.string() }),
  output: z.object({
    // Null when the workspace has no workflow database or no run.
    run: z.object({ runId: z.string(), state: z.string() }).nullable(),
    tasks: z.array(taskSchema),
    message: z.string().nullable(),
  }),
});

export type WorkflowStatus = z.infer<typeof workflowStatus.output>;
