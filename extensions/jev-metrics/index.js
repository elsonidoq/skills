import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";

import { aggregateActiveBranch, COVERAGE, CUSTOM_ENTRY_TYPE } from "./lib/aggregate.js";
import { appendCloseout, readHistory } from "./lib/csv-store.js";
import {
	APPROVED_SKILL_IDS,
	DISPOSITIONS,
	createDisposition,
	createInvalidEvent,
	validateEvent,
} from "./lib/events.js";
import { JevInputError, runJevRanking } from "./lib/jev-client.js";

export const COVERAGE_NOTICE = "Only jev_rank calls are tracked; raw shell and MCP calls are untracked.";

const RANK_PARAMETERS = {
	type: "object",
	additionalProperties: false,
	required: ["skillId", "criterion", "candidates"],
	properties: {
		skillId: { type: "string", enum: APPROVED_SKILL_IDS },
		criterion: { type: "string", minLength: 1, maxLength: 4096 },
		candidates: {
			type: "array",
			minItems: 2,
			maxItems: 50,
			items: {
				type: "object",
				additionalProperties: false,
				required: ["candidateId", "body"],
				properties: {
					candidateId: { type: "string", pattern: "^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$" },
					body: { type: "string" },
				},
			},
		},
	},
};
const DISPOSITION_PARAMETERS = {
	type: "object",
	additionalProperties: false,
	required: ["proposalId", "disposition"],
	properties: {
		proposalId: { type: "string", minLength: 1, maxLength: 384 },
		disposition: { type: "string", enum: DISPOSITIONS },
	},
};
const METRICS_PARAMETERS = {
	type: "object",
	additionalProperties: false,
	required: ["action"],
	properties: {
		action: { type: "string", enum: ["current", "history", "closeout"] },
	},
};

function defaultClock() {
	return { iso: () => new Date().toISOString() };
}

function defaultUuid() {
	return { next: () => randomUUID() };
}

/** Node child-process adapter used only at the configured `jev run -` boundary. */
export function createProcessAdapter() {
	return {
		run(command, args, { input = "", signal } = {}) {
			return new Promise((resolve, reject) => {
				const child = spawn(command, args, {
					stdio: ["pipe", "pipe", "pipe"],
					shell: false,
					signal,
				});
				let stdout = "";
				let stderr = "";
				child.stdout.setEncoding("utf8");
				child.stderr.setEncoding("utf8");
				child.stdout.on("data", (chunk) => { stdout += chunk; });
				child.stderr.on("data", (chunk) => { stderr += chunk; });
				child.once("error", reject);
				child.once("close", (code, processSignal) => resolve({
					code: code ?? 1,
					stdout,
					stderr,
					signal: processSignal,
				}));
				child.stdin.end(input, "utf8");
			});
		},
	};
}

function textResult(details) {
	return {
		content: [{ type: "text", text: JSON.stringify(details) }],
		details,
	};
}

function counters(summary) {
	return {
		attempts: summary.attempts,
		successes: summary.successes,
		proposals: summary.proposals,
		accepted: summary.accepted,
		overridden: summary.overridden,
		notUsed: summary.notUsed,
		pending: summary.pending,
		invalidEvents: summary.invalidEvents,
	};
}

function currentResult(aggregate) {
	return {
		sessionId: aggregate.sessionId,
		leafId: aggregate.leafId,
		coverage: COVERAGE,
		coverageNotice: COVERAGE_NOTICE,
		eventState: aggregate.eventState,
		total: counters(aggregate.total),
		bySkill: aggregate.bySkill.map((summary) => ({ scope: summary.scope, ...counters(summary) })),
	};
}

function activeAggregate(ctx) {
	return aggregateActiveBranch(ctx.sessionManager.getBranch(), {
		sessionId: ctx.sessionManager.getSessionId(),
		leafId: ctx.sessionManager.getLeafId(),
		customType: CUSTOM_ENTRY_TYPE,
	});
}

function activeEventData(ctx) {
	return ctx.sessionManager.getBranch()
		.filter((entry) => entry?.type === "custom" && entry.customType === CUSTOM_ENTRY_TYPE)
		.map((entry) => entry.data);
}

function drawUuid(source) {
	if (typeof source === "function") return source();
	if (typeof source?.next === "function") return source.next();
	if (typeof source?.uuid === "function") return source.uuid();
	throw new TypeError("uuid source is required");
}

function branchUniqueUuid(ctx, source) {
	const used = new Set();
	for (const event of activeEventData(ctx)) {
		if (typeof event?.eventId === "string") used.add(event.eventId);
		if (typeof event?.invocationId === "string") used.add(event.invocationId);
	}
	return {
		next() {
			for (let attempt = 0; attempt < 100; attempt += 1) {
				const value = drawUuid(source);
				if (used.has(value)) continue;
				used.add(value);
				return value;
			}
			throw new RangeError("could not generate a unique session-branch UUID");
		},
	};
}

function findProposalContext(ctx, proposalId) {
	const sessionId = ctx.sessionManager.getSessionId();
	const allEvents = activeEventData(ctx);
	const hasCrossSessionProposal = allEvents.some((event) =>
		event?.eventType === "invocation_terminal" && event.sessionId !== sessionId &&
		Array.isArray(event.proposals) && event.proposals.some((proposal) => proposal?.proposalId === proposalId));
	const unique = [];
	const eventIds = new Set();
	for (const event of allEvents) {
		try { validateEvent(event, { sessionId }); } catch { continue; }
		if (eventIds.has(event.eventId)) continue;
		eventIds.add(event.eventId);
		unique.push(event);
	}
	const starts = new Map();
	for (const event of unique) {
		if (event.eventType === "invocation_started" && !starts.has(event.invocationId)) starts.set(event.invocationId, event);
	}
	const terminals = new Map();
	for (const event of unique) {
		if (event.eventType !== "invocation_terminal" || terminals.has(event.invocationId)) continue;
		const start = starts.get(event.invocationId);
		if (!start) continue;
		try { validateEvent(event, { sessionId, start }); } catch { continue; }
		terminals.set(event.invocationId, event);
	}
	for (const [invocationId, terminal] of terminals) {
		if (terminal.status !== "succeeded") continue;
		const proposal = terminal.proposals.find(({ proposalId: id }) => id === proposalId);
		if (!proposal) continue;
		const start = starts.get(invocationId);
		let existingDisposition;
		for (const event of unique) {
			if (event.eventType !== "proposal_disposition" || event.proposalId !== proposalId) continue;
			if (event.skillId !== start.skillId) continue;
			existingDisposition = event;
			break;
		}
		return { proposal, start, terminal, existingDisposition };
	}
	return { reason: hasCrossSessionProposal ? "cross_session" : "unknown_proposal" };
}

function renderSummaryLine(label, summary) {
	return `${label}: successes ${summary.successes} / ${summary.attempts} attempts; ` +
		`proposals ${summary.proposals}; accepted ${summary.accepted} / ${summary.proposals} proposals; ` +
		`overridden ${summary.overridden} / ${summary.proposals} proposals; ` +
		`not used ${summary.notUsed} / ${summary.proposals} proposals; ` +
		`pending ${summary.pending} / ${summary.proposals} proposals; invalid events ${summary.invalidEvents}`;
}

export function renderCurrentMetrics(result) {
	const lines = [
		"Jev metrics (active branch)",
		`Session: ${result.sessionId}`,
		`Leaf: ${result.leafId ?? "(none)"}`,
		`Event state: ${result.eventState}`,
		`Coverage: ${result.coverage} — ${result.coverageNotice}`,
		renderSummaryLine("Total", result.total),
	];
	for (const summary of result.bySkill) lines.push(renderSummaryLine(summary.scope, summary));
	return lines.join("\n");
}

export function renderHistoryMetrics(result) {
	const lines = [
		`Jev metrics history store: ${result.storeState}`,
		`Coverage: ${result.coverage} — ${COVERAGE_NOTICE}`,
	];
	if (result.storeState === "available") {
		for (const row of result.rows) {
			lines.push(`${row.session_id}: successes ${row.successes} / ${row.attempts} attempts; ` +
				`accepted ${row.accepted} / ${row.proposals} proposals; overridden ${row.overridden} / ${row.proposals}; ` +
				`not used ${row.not_used} / ${row.proposals}; pending ${row.pending} / ${row.proposals}`);
		}
	}
	return lines.join("\n");
}

export function renderMetricsHelp() {
	return [
		"/jev-metrics — current active-branch metrics",
		"/jev-metrics history — validated cross-session history",
		"/jev-metrics help — this help",
		"Counters: attempts, successes, proposals, accepted, overridden, not used, pending, invalid events.",
		"Denominators are always shown as successes / attempts and dispositions / proposals.",
		`Coverage: ${COVERAGE}. ${COVERAGE_NOTICE}`,
		"Privacy: candidate bodies, criteria, prompts, logs, credentials, personal data, raw responses, stderr, and provider endpoints are not stored.",
	].join("\n");
}

/** Create an injectable Pi 0.87.x extension factory for deterministic testing. */
export function createJevMetricsExtension({
	processAdapter = createProcessAdapter(),
	clock = defaultClock(),
	uuid = defaultUuid(),
	executable = "jev",
	stateHome,
	fileSystem,
} = {}) {
	return function jevMetricsExtension(pi) {
		let snapshot;
		let mutationQueue = Promise.resolve();
		const reconstruct = (ctx) => {
			snapshot = activeAggregate(ctx);
			return snapshot;
		};
		const serialize = (operation) => {
			const result = mutationQueue.then(operation, operation);
			mutationQueue = result.catch(() => undefined);
			return result;
		};
		const appendInvalid = (ctx, operation, reason) => {
			const event = createInvalidEvent({
				sessionId: ctx.sessionManager.getSessionId(),
				operation,
				reason,
			}, { clock, uuid: branchUniqueUuid(ctx, uuid) });
			pi.appendEntry(CUSTOM_ENTRY_TYPE, event);
			reconstruct(ctx);
			return event;
		};

		pi.on("session_start", async (_event, ctx) => { reconstruct(ctx); });
		pi.on("session_tree", async (_event, ctx) => { reconstruct(ctx); });

		pi.registerTool({
			name: "jev_rank",
			label: "Jev Rank",
			description: "Advisory ranking for 2–50 explicit candidates. Only this instrumented tool is tracked.",
			parameters: RANK_PARAMETERS,
			async execute(_toolCallId, params, signal, _onUpdate, ctx) {
				return serialize(async () => {
					try {
						const { start, terminal } = await runJevRanking({
							sessionId: ctx.sessionManager.getSessionId(),
							...params,
						}, {
							processAdapter,
							clock,
							uuid: branchUniqueUuid(ctx, uuid),
							executable,
							signal,
							onEvent: async (event) => {
								pi.appendEntry(CUSTOM_ENTRY_TYPE, event);
								reconstruct(ctx);
							},
						});
						const result = {
							tracked: true,
							invocationId: start.invocationId,
							status: terminal.status,
							proposals: terminal.proposals,
							coverage: COVERAGE,
						};
						if (terminal.failureClass) result.failureClass = terminal.failureClass;
						if (terminal.status === "succeeded") {
							result.requiredNextAction = "Record one disposition for each proposal after main-agent review.";
						} else {
							result.fallback = "Use the complete original candidate set manually.";
						}
						return textResult(result);
					} catch (error) {
						if (!(error instanceof JevInputError) && error?.reason !== "input" && error?.reason !== "schema_invalid") throw error;
						appendInvalid(ctx, "rank", "schema_invalid");
						return textResult({
							tracked: false,
							status: "malformed",
							failureClass: "input",
							proposals: [],
							fallback: "Use the complete original candidate set manually.",
							coverage: COVERAGE,
						});
					}
				});
			},
		});

		pi.registerTool({
			name: "jev_disposition",
			label: "Jev Disposition",
			description: "Record the first valid accepted, overridden, or not-used outcome for one proposal.",
			parameters: DISPOSITION_PARAMETERS,
			async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
				return serialize(async () => {
					const context = findProposalContext(ctx, params.proposalId);
					if (context.reason) {
						appendInvalid(ctx, "disposition", context.reason);
						return textResult({ recorded: false, reason: context.reason });
					}
					try {
						const created = createDisposition({
							proposalId: params.proposalId,
							sessionId: ctx.sessionManager.getSessionId(),
							skillId: context.start.skillId,
							disposition: params.disposition,
						}, { clock, uuid: branchUniqueUuid(ctx, uuid), ...context });
						if (!created.idempotentReplay) {
							pi.appendEntry(CUSTOM_ENTRY_TYPE, created.event);
							reconstruct(ctx);
						}
						return textResult({
							recorded: true,
							idempotentReplay: created.idempotentReplay,
							proposalId: params.proposalId,
							disposition: params.disposition,
						});
					} catch (error) {
						const reason = error?.reason === "conflicting_disposition" ? "conflicting_disposition" : "schema_invalid";
						appendInvalid(ctx, "disposition", reason);
						return textResult({ recorded: false, reason });
					}
				});
			},
		});

		pi.registerTool({
			name: "jev_metrics",
			label: "Jev Metrics",
			description: "Retrieve current/history metrics or append one idempotent finish-session closeout row. Never invokes Jev.",
			parameters: METRICS_PARAMETERS,
			async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
				if (params.action === "current") return textResult(currentResult(reconstruct(ctx)));
				if (params.action === "history") {
					const history = await readHistory({ projectRoot: ctx.cwd, stateHome, fileSystem });
					return textResult({ ...history, coverage: COVERAGE });
				}
				if (params.action === "closeout") {
					return serialize(async () => {
						let aggregate = reconstruct(ctx);
						if (["corrupt", "unsupported"].includes(aggregate.eventState)) {
							return textResult({
								status: "store_error",
								sessionId: aggregate.sessionId,
								storeState: "invalid",
								total: counters(aggregate.total),
							});
						}
						const closeout = await appendCloseout(aggregate, {
							projectRoot: ctx.cwd,
							stateHome,
							fileSystem,
							clock,
						});
						if (closeout.status === "store_error") {
							appendInvalid(ctx, "closeout", closeout.storeState === "invalid" ? "store_invalid" : "store_unreadable");
							aggregate = reconstruct(ctx);
						}
						return textResult({ ...closeout, total: counters(aggregate.total), coverage: COVERAGE });
					});
				}
				return textResult({ status: "store_error", reason: "schema_invalid", coverage: COVERAGE });
			},
		});

		pi.registerCommand("jev-metrics", {
			description: "Show current Jev metrics, history, or help",
			handler: async (args, ctx) => {
				const action = args.trim().toLowerCase() || "current";
				let output;
				if (action === "help") output = renderMetricsHelp();
				else if (action === "history") {
					const history = await readHistory({ projectRoot: ctx.cwd, stateHome, fileSystem });
					output = renderHistoryMetrics({ ...history, coverage: COVERAGE });
				} else if (action === "current") output = renderCurrentMetrics(currentResult(reconstruct(ctx)));
				else output = `${renderMetricsHelp()}\nUnknown action: ${action}`;
				ctx.ui?.notify?.(output, action === "help" ? "info" : "info");
				return output;
			},
		});
	};
}

export default createJevMetricsExtension();
