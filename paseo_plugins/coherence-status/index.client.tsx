import type { PluginClientContext } from "@getpaseo/plugin/client";
import { WorkflowStatusPanel } from "./client/status-panel";

export default function contribute(client: PluginClientContext) {
  client.addWorkspacePanel({
    id: "coherence-status",
    title: "Workflow status",
    icon: "ListChecks",
    context: "workspace",
    locations: ["workspace", "explorer"],
    Component: WorkflowStatusPanel,
  });

  client.addCommandCenterItem({
    id: "coherence-status-open",
    title: "Show workflow status",
    icon: "ListChecks",
    keywords: ["coherence", "workflow", "tasks", "status", "progress"],
    context: "workspace",
    onSelect(context) {
      context.openPanel("coherence-status", { location: "workspace" });
    },
  });

  return () => {};
}
