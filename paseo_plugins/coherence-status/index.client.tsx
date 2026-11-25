import type { PluginButtonRegistration, PluginClientContext } from "@getpaseo/plugin/client";
import { WorkflowStatusPanel } from "./client/status-panel";
import { workflowStatus } from "./shared/status";

const PANEL_ID = "coherence-status";

export default function contribute(client: PluginClientContext) {
  client.addWorkspacePanel({
    id: PANEL_ID,
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
      context.openPanel(PANEL_ID, { location: "workspace" });
    },
  });

  // One-tap access on mobile: a composer pill beside Tasks and Subagents, only in
  // workspaces that have a Coherence workflow run.
  const pills = new Map<string, PluginButtonRegistration>();
  const lifetime = new AbortController();
  const register = async (agent: { id: string; workspaceId?: string | null }) => {
    const workspaceId = agent.workspaceId;
    if (lifetime.signal.aborted || !workspaceId || pills.has(agent.id)) return;
    const status = await client.rpc(workflowStatus, { workspaceId }).catch(() => null);
    if (lifetime.signal.aborted || !status?.run || pills.has(agent.id)) return;
    pills.set(
      agent.id,
      client.addComposerPill({
        id: "coherence-status",
        workspaceId,
        agentId: agent.id,
        button: {
          title: "Show workflow status",
          icon: "ListChecks",
          label: "Workflow",
          behavior: {
            kind: "action",
            onPress() {
              client.openPanel(PANEL_ID, { workspaceId, agentId: agent.id });
            },
          },
        },
      }),
    );
  };
  const removeAll = () => {
    for (const pill of pills.values()) pill.remove();
    pills.clear();
  };
  void client.paseo.agents
    .list({ subscribe: {}, signal: lifetime.signal })
    .then(({ subscription }) => {
      subscription.subscribe({
        snapshot: ({ entries }) => {
          removeAll();
          for (const { agent } of entries) void register(agent);
        },
        update: (message) => {
          if (message.type !== "agent_update") return;
          const update = message.payload;
          if (update.kind === "upsert") return void register(update.agent);
          pills.get(update.agentId)?.remove();
          pills.delete(update.agentId);
        },
      });
      return undefined;
    })
    .catch((error) => {
      if (!lifetime.signal.aborted) console.error("Agent observation failed", error);
    });

  return () => {
    lifetime.abort();
    removeAll();
  };
}
