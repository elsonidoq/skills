Shows the status of the Coherence workflow in the current workspace: each task, its state
(pending, running, complete, failed or interrupted) and the time it started.

Tap the "Workflow" pill in the composer bar, beside Tasks and Subagents. The pill appears only
in workspaces that have a Coherence workflow run. You can also select "Show workflow status"
in the command center.
The panel refreshes every five seconds while the run is active.

The daemon reads `.coherence/workflow/workflow.sqlite` in the workspace directory, read-only.
It shows the running run, or else the run with the most recent activity. It requires a
daemon on Node.js 22.13 or later for the built-in `node:sqlite` module.
