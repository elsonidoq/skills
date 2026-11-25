import type { PluginServerContext } from "@getpaseo/plugin/server";
import { readWorkflowStatus } from "./server/status";
import { workflowStatus } from "./shared/status";

export default function contribute(server: PluginServerContext) {
  server.handle(workflowStatus, async ({ workspaceId }, { paseo }) => {
    const workspace = await paseo.workspaces.ref(workspaceId).refresh();
    const directory = workspace?.workspaceDirectory ?? workspace?.projectRootPath;
    if (!directory) {
      return { run: null, tasks: [], message: `Unknown workspace ${workspaceId}.` };
    }
    return readWorkflowStatus(directory);
  });
  return () => {};
}
