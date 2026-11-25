import type { PluginTheme } from "@getpaseo/plugin";
import type { PluginWorkspacePanelProps } from "@getpaseo/plugin/client";
import { useRpc } from "@getpaseo/plugin/client";
import { ScrollView } from "@getpaseo/plugin/client/react-native";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { Pressable, Text, View } from "react-native";
import { workflowStatus } from "../shared/status";

const REFRESH_MS = 5000;

function stateColor(state: string, colors: PluginTheme["colors"]): string {
  if (state === "complete") return colors.statusSuccess;
  if (state === "running") return colors.accent;
  if (state === "failed") return colors.statusDanger;
  if (state === "interrupted") return colors.statusWarning;
  return colors.foregroundMuted;
}

function formatStart(epochMs: number | null): string {
  if (epochMs === null) return "";
  const date = new Date(epochMs);
  const time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (date.toDateString() === new Date().toDateString()) return time;
  return `${date.toLocaleDateString([], { month: "short", day: "numeric" })} ${time}`;
}

export function WorkflowStatusPanel({ theme, layout, workspaceId }: PluginWorkspacePanelProps) {
  const read = useRpc(workflowStatus);
  const query = useQuery({
    queryKey: ["coherence-status", workspaceId],
    queryFn: () => read({ workspaceId }),
    // Poll only while the run is active.
    refetchInterval: (current) => (current.state.data?.run?.state === "running" ? REFRESH_MS : false),
  });
  const styles = useMemo(
    () => ({
      content: { padding: layout.compact ? 12 : 16, gap: 8 },
      header: { flexDirection: "row" as const, justifyContent: "space-between" as const, alignItems: "center" as const },
      title: { color: theme.colors.foreground, fontSize: 15, fontWeight: "600" as const, flexShrink: 1 },
      muted: { color: theme.colors.foregroundMuted, fontSize: 13 },
      row: {
        flexDirection: "row" as const,
        alignItems: "center" as const,
        gap: 10,
        paddingVertical: 8,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
      },
      dot: { width: 10, height: 10, borderRadius: 5 },
      taskId: { color: theme.colors.foreground, fontSize: 14, flex: 1 },
      state: { fontSize: 13, minWidth: 80 },
      time: { color: theme.colors.foregroundMuted, fontSize: 13, minWidth: 48, textAlign: "right" as const },
      error: { color: theme.colors.statusDanger, fontSize: 13 },
    }),
    [theme, layout.compact],
  );

  const data = query.data;
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text numberOfLines={1} style={styles.title}>
          {data?.run ? `${data.run.runId} · ${data.run.state}` : "Workflow status"}
        </Text>
        <Pressable accessibilityRole="button" accessibilityLabel="Refresh workflow status" onPress={() => query.refetch()}>
          <Text style={[styles.muted, { color: theme.colors.accent }]}>{query.isFetching ? "Refreshing…" : "Refresh"}</Text>
        </Pressable>
      </View>
      {query.isLoading ? <Text style={styles.muted}>Loading…</Text> : null}
      {query.isError ? (
        <Text style={styles.error}>
          Cannot read workflow status: {query.error instanceof Error ? query.error.message : String(query.error)}
        </Text>
      ) : null}
      {data?.message ? <Text style={styles.muted}>{data.message}</Text> : null}
      {data?.tasks.map((task) => {
        const color = stateColor(task.state, theme.colors);
        return (
          <View key={task.taskId} style={styles.row}>
            <View style={[styles.dot, { backgroundColor: color }]} />
            <Text numberOfLines={1} style={styles.taskId}>
              {task.taskId}
            </Text>
            <Text style={[styles.state, { color }]}>{task.state}</Text>
            <Text style={styles.time}>{formatStart(task.startedAt)}</Text>
          </View>
        );
      })}
    </ScrollView>
  );
}
