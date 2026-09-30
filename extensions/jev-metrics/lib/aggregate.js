import { APPROVED_SKILL_IDS, SCHEMA_VERSION, validateEvent } from "./events.js";

export const CUSTOM_ENTRY_TYPE = "jev-metrics";
export const COVERAGE = "instrumented-only";

function issue(issues, flags, reason, event = undefined, kind = "corrupt") {
	const detail = { reason };
	if (event?.eventId) detail.eventId = event.eventId;
	if (event?.invocationId) detail.invocationId = event.invocationId;
	if (event?.proposalId) detail.proposalId = event.proposalId;
	issues.push(Object.freeze(detail));
	flags[kind] = true;
}

function sameValue(left, right) {
	try {
		return JSON.stringify(left) === JSON.stringify(right);
	} catch {
		return false;
	}
}

function emptyCounters() {
	return {
		attempts: 0,
		successes: 0,
		proposals: 0,
		accepted: 0,
		overridden: 0,
		notUsed: 0,
		pending: 0,
		invalidEvents: 0,
	};
}

function summarize({ sessionId, leafId, scope, starts, terminals, dispositions, invalidEvents }) {
	const counters = emptyCounters();
	const scopedStarts = scope === "session"
		? [...starts.values()]
		: [...starts.values()].filter((start) => start.skillId === scope);
	const invocationIds = new Set(scopedStarts.map(({ invocationId }) => invocationId));
	counters.attempts = scopedStarts.length;

	const proposalIds = new Set();
	for (const invocationId of invocationIds) {
		const terminal = terminals.get(invocationId);
		if (terminal?.status !== "succeeded") continue;
		counters.successes += 1;
		for (const proposal of terminal.proposals) proposalIds.add(proposal.proposalId);
	}
	counters.proposals = proposalIds.size;

	for (const proposalId of proposalIds) {
		const disposition = dispositions.get(proposalId);
		if (!disposition) continue;
		if (disposition.disposition === "accepted") counters.accepted += 1;
		else if (disposition.disposition === "overridden") counters.overridden += 1;
		else if (disposition.disposition === "not_used") counters.notUsed += 1;
	}
	counters.pending = counters.proposals - counters.accepted - counters.overridden - counters.notUsed;
	counters.invalidEvents = scope === "session" ? invalidEvents : 0;

	return Object.freeze({
		sessionId,
		leafId,
		scope,
		...counters,
		coverage: COVERAGE,
	});
}

function classifyState(flags) {
	if (flags.corrupt) return "corrupt";
	if (flags.unsupported) return "unsupported";
	if (flags.orphaned) return "orphaned";
	return "available";
}

/**
 * Reconstruct metrics from event data already selected from the active branch.
 * Invalid persisted values are reported by stable reason only and never counted.
 */
export function aggregateEvents(events, { sessionId, leafId = null } = {}) {
	if (!Array.isArray(events)) throw new TypeError("events must be an array");
	if (typeof sessionId !== "string" || sessionId.length === 0) {
		throw new TypeError("sessionId must be the current non-empty Pi session ID");
	}
	if (leafId !== null && typeof leafId !== "string") throw new TypeError("leafId must be a string or null");

	const issues = [];
	const flags = { corrupt: false, unsupported: false, orphaned: false };
	const uniqueEvents = [];
	const eventsById = new Map();

	for (const event of events) {
		if (event && typeof event === "object" && !Array.isArray(event) &&
			Object.hasOwn(event, "schemaVersion") && event.schemaVersion !== SCHEMA_VERSION) {
			issue(issues, flags, "unsupported_schema", event, "unsupported");
			continue;
		}
		try {
			validateEvent(event);
		} catch {
			issue(issues, flags, "corrupt_event", event);
			continue;
		}
		if (event.sessionId !== sessionId) {
			issue(issues, flags, "cross_session", event);
			continue;
		}
		const previous = eventsById.get(event.eventId);
		if (previous) {
			if (!sameValue(previous, event)) issue(issues, flags, "duplicate_event_id", event);
			continue;
		}
		eventsById.set(event.eventId, event);
		uniqueEvents.push(event);
	}

	const starts = new Map();
	for (const event of uniqueEvents) {
		if (event.eventType !== "invocation_started") continue;
		if (starts.has(event.invocationId)) {
			issue(issues, flags, "duplicate_start", event);
			continue;
		}
		starts.set(event.invocationId, event);
	}

	const terminals = new Map();
	for (const event of uniqueEvents) {
		if (event.eventType !== "invocation_terminal") continue;
		const start = starts.get(event.invocationId);
		if (!start) {
			issue(issues, flags, "orphan_terminal", event);
			continue;
		}
		try {
			validateEvent(event, { sessionId, start });
		} catch {
			issue(issues, flags, "invalid_terminal", event);
			continue;
		}
		if (terminals.has(event.invocationId)) {
			issue(issues, flags, "duplicate_terminal", event);
			continue;
		}
		terminals.set(event.invocationId, event);
	}

	const proposals = new Map();
	for (const [invocationId, terminal] of terminals) {
		if (terminal.status !== "succeeded") continue;
		const start = starts.get(invocationId);
		for (const proposal of terminal.proposals) {
			proposals.set(proposal.proposalId, Object.freeze({ proposal, start }));
		}
	}

	const dispositions = new Map();
	for (const event of uniqueEvents) {
		if (event.eventType !== "proposal_disposition") continue;
		const context = proposals.get(event.proposalId);
		if (!context) {
			issue(issues, flags, "unknown_proposal", event);
			continue;
		}
		if (event.sessionId !== context.start.sessionId) {
			issue(issues, flags, "cross_session", event);
			continue;
		}
		if (event.skillId !== context.start.skillId) {
			issue(issues, flags, "skill_mismatch", event);
			continue;
		}
		const previous = dispositions.get(event.proposalId);
		if (!previous) {
			dispositions.set(event.proposalId, event);
			continue;
		}
		if (previous.disposition !== event.disposition) {
			issue(issues, flags, "conflicting_disposition", event);
		}
	}

	let invalidEvents = 0;
	for (const event of uniqueEvents) {
		if (event.eventType === "invalid_event") invalidEvents += 1;
	}

	for (const start of starts.values()) {
		if (!terminals.has(start.invocationId)) {
			issue(issues, flags, "orphan_start", start, "orphaned");
		}
	}

	const summaryInput = { sessionId, leafId, starts, terminals, dispositions, invalidEvents };
	const total = summarize({ ...summaryInput, scope: "session" });
	const representedSkills = new Set([...starts.values()].map(({ skillId }) => skillId));
	const bySkill = APPROVED_SKILL_IDS
		.filter((skillId) => representedSkills.has(skillId))
		.map((skillId) => summarize({ ...summaryInput, scope: skillId }));

	return Object.freeze({
		sessionId,
		leafId,
		coverage: COVERAGE,
		eventState: classifyState(flags),
		total,
		bySkill: Object.freeze(bySkill),
		issues: Object.freeze(issues),
	});
}

/** Select only this extension's owned custom entries from Pi's current getBranch() result. */
export function aggregateActiveBranch(
	branchEntries,
	{ sessionId, leafId = null, customType = CUSTOM_ENTRY_TYPE } = {},
) {
	if (!Array.isArray(branchEntries)) throw new TypeError("branchEntries must be an array");
	if (typeof customType !== "string" || customType.length === 0) throw new TypeError("customType must be non-empty");
	const events = [];
	for (const entry of branchEntries) {
		if (!entry || entry.type !== "custom" || entry.customType !== customType) continue;
		events.push(entry.data);
	}
	return aggregateEvents(events, { sessionId, leafId });
}
