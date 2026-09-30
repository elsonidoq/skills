export const APPROVED_SKILL_IDS = Object.freeze([
	"scientific-method-debugging",
	"receiving-code-review",
	"coordinate-implementation",
	"track-open-issue",
	"speckit-analyze",
	"speckit-checklist",
	"speckit-clarify",
	"speckit-tasks",
]);
export const TERMINAL_STATUSES = Object.freeze(["succeeded", "unavailable", "failed", "malformed"]);
export const FAILURE_CLASSES = Object.freeze([
	"cli_missing",
	"auth",
	"input",
	"provider",
	"retryable",
	"cancelled",
	"response_schema",
]);
export const DISPOSITIONS = Object.freeze(["accepted", "overridden", "not_used"]);
export const INVALID_OPERATIONS = Object.freeze(["rank", "disposition", "closeout"]);
export const INVALID_REASONS = Object.freeze([
	"duplicate_terminal",
	"unknown_proposal",
	"cross_session",
	"conflicting_disposition",
	"schema_invalid",
	"store_missing",
	"store_unreadable",
	"store_invalid",
]);

export const SCHEMA_VERSION = 1;
export const CANDIDATE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$/;

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const DATE_TIME_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
const BASE_FIELDS = ["schemaVersion", "eventType", "eventId", "sessionId"];
const EVENT_FIELDS = Object.freeze({
	invocation_started: [...BASE_FIELDS, "invocationId", "skillId", "startedAt", "candidateIds"],
	invocation_terminal: [...BASE_FIELDS, "invocationId", "finishedAt", "status", "failureClass", "proposals"],
	proposal_disposition: [...BASE_FIELDS, "proposalId", "skillId", "disposition", "recordedAt"],
	invalid_event: [...BASE_FIELDS, "operation", "reason", "recordedAt"],
});
const PROPOSAL_FIELDS = ["proposalId", "candidateId", "rank", "score", "confidence"];

export class EventValidationError extends TypeError {
	constructor(message, reason = "schema_invalid") {
		super(message);
		this.name = "EventValidationError";
		this.reason = reason;
	}
}

function fail(message, reason) {
	throw new EventValidationError(message, reason);
}

function isObject(value) {
	return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assertObject(value, label) {
	if (!isObject(value)) fail(`${label} must be an object`);
}

function assertExactFields(value, allowed, required, label) {
	for (const field of required) {
		if (!Object.hasOwn(value, field)) fail(`${label}.${field} is required`);
	}
	for (const field of Object.keys(value)) {
		if (!allowed.includes(field)) fail(`${label}.${field} is unexpected`);
	}
}

function assertEnum(value, values, label) {
	if (!values.includes(value)) fail(`${label} is invalid`);
}

function assertUuid(value, label) {
	if (typeof value !== "string" || !UUID_PATTERN.test(value)) fail(`${label} must be a UUID`);
}

function assertSessionId(value) {
	if (typeof value !== "string" || value.length < 1 || value.length > 256) {
		fail("sessionId must be a non-empty string of at most 256 characters");
	}
}

function assertTimestamp(value, label) {
	if (typeof value !== "string" || !DATE_TIME_PATTERN.test(value) || !Number.isFinite(Date.parse(value))) {
		fail(`${label} must be an ISO-8601 date-time`);
	}
}

function assertCandidateId(value, label = "candidateId") {
	if (typeof value !== "string" || !CANDIDATE_ID_PATTERN.test(value)) {
		fail(`${label} is invalid`);
	}
}

function assertCandidateIds(candidateIds) {
	if (!Array.isArray(candidateIds) || candidateIds.length < 2 || candidateIds.length > 50) {
		fail("candidateIds must contain 2 through 50 entries");
	}
	const seen = new Set();
	for (const candidateId of candidateIds) {
		assertCandidateId(candidateId);
		if (seen.has(candidateId)) fail("candidateIds must be unique");
		seen.add(candidateId);
	}
}

function assertProposal(proposal, invocationId, proposalCount) {
	assertObject(proposal, "proposal");
	assertExactFields(proposal, PROPOSAL_FIELDS, ["proposalId", "candidateId", "rank", "score"], "proposal");
	assertCandidateId(proposal.candidateId);
	const expectedId = `${invocationId}:proposal:${proposal.candidateId}`;
	if (proposal.proposalId !== expectedId || proposal.proposalId.length > 384) {
		fail("proposal.proposalId must use invocationId:proposal:candidateId");
	}
	if (!Number.isInteger(proposal.rank) || proposal.rank < 1 || proposal.rank > proposalCount) {
		fail("proposal.rank must be a unique integer from 1 through candidate count");
	}
	if (!Number.isFinite(proposal.score)) fail("proposal.score must be finite");
	if (Object.hasOwn(proposal, "confidence") &&
		(!Number.isFinite(proposal.confidence) || proposal.confidence < 0 || proposal.confidence > 1)) {
		fail("proposal.confidence must be finite and between 0 and 1");
	}
}

function assertProposals(event) {
	if (!Array.isArray(event.proposals) || event.proposals.length > 50) fail("proposals must be an array of at most 50 entries");
	if (event.status !== "succeeded") {
		if (event.proposals.length !== 0) fail("proposals must be empty for a non-success terminal");
		return;
	}
	if (event.proposals.length < 2) fail("proposals must include exactly one proposal per candidate on success");
	const candidateIds = new Set();
	const ranks = new Set();
	for (const proposal of event.proposals) {
		assertProposal(proposal, event.invocationId, event.proposals.length);
		if (candidateIds.has(proposal.candidateId)) fail("proposal candidateIds must be unique");
		if (ranks.has(proposal.rank)) fail("proposal ranks must be unique");
		candidateIds.add(proposal.candidateId);
		ranks.add(proposal.rank);
	}
}

function validateStart(event) {
	assertExactFields(event, EVENT_FIELDS.invocation_started, EVENT_FIELDS.invocation_started, "InvocationStart");
	assertUuid(event.invocationId, "invocationId");
	assertEnum(event.skillId, APPROVED_SKILL_IDS, "skillId");
	assertTimestamp(event.startedAt, "startedAt");
	assertCandidateIds(event.candidateIds);
}

function validateTerminal(event) {
	const required = EVENT_FIELDS.invocation_terminal.filter((field) => field !== "failureClass");
	assertExactFields(event, EVENT_FIELDS.invocation_terminal, required, "InvocationTerminal");
	assertUuid(event.invocationId, "invocationId");
	assertTimestamp(event.finishedAt, "finishedAt");
	assertEnum(event.status, TERMINAL_STATUSES, "status");
	if (event.status === "succeeded") {
		if (Object.hasOwn(event, "failureClass")) fail("failureClass must be absent for succeeded terminals");
	} else if (Object.hasOwn(event, "failureClass")) {
		assertEnum(event.failureClass, FAILURE_CLASSES, "failureClass");
	}
	assertProposals(event);
}

function validateDisposition(event) {
	assertExactFields(event, EVENT_FIELDS.proposal_disposition, EVENT_FIELDS.proposal_disposition, "Disposition");
	if (typeof event.proposalId !== "string" || event.proposalId.length < 1 || event.proposalId.length > 384) {
		fail("proposalId must be a non-empty string of at most 384 characters");
	}
	assertEnum(event.skillId, APPROVED_SKILL_IDS, "skillId");
	assertEnum(event.disposition, DISPOSITIONS, "disposition");
	assertTimestamp(event.recordedAt, "recordedAt");
}

function validateInvalidEvent(event) {
	assertExactFields(event, EVENT_FIELDS.invalid_event, EVENT_FIELDS.invalid_event, "InvalidEvent");
	assertEnum(event.operation, INVALID_OPERATIONS, "operation");
	assertEnum(event.reason, INVALID_REASONS, "reason");
	assertTimestamp(event.recordedAt, "recordedAt");
}

function collectionHas(collection, value) {
	if (!collection) return false;
	if (typeof collection.has === "function") return collection.has(value);
	return Array.from(collection).includes(value);
}

function validateContext(event, context) {
	if (context.sessionId !== undefined && event.sessionId !== context.sessionId) {
		fail("sessionId must equal the current Pi session ID", "cross_session");
	}
	if (collectionHas(context.eventIds, event.eventId)) fail("eventId must be unique within the session branch");
	if (event.eventType === "invocation_started" && collectionHas(context.invocationIds, event.invocationId)) {
		fail("invocationId must be unique within the session branch");
	}
	if (event.eventType === "invocation_terminal" && context.start) {
		const { start } = context;
		validateEvent(start, context.sessionId === undefined ? {} : { sessionId: context.sessionId });
		if (start.eventType !== "invocation_started" || event.invocationId !== start.invocationId) {
			fail("invocationId must reference one start event");
		}
		if (event.sessionId !== start.sessionId) fail("sessionId must equal the referenced start", "cross_session");
		if (Date.parse(event.finishedAt) < Date.parse(start.startedAt)) fail("finishedAt must not be earlier than startedAt");
		if (event.status === "succeeded") {
			if (event.proposals.length !== start.candidateIds.length) fail("proposals must contain exactly one entry per candidate");
			const candidateIds = new Set(event.proposals.map(({ candidateId }) => candidateId));
			if (start.candidateIds.some((candidateId) => !candidateIds.has(candidateId))) {
				fail("proposal candidateId must occur in the referenced start event");
			}
		}
	}
}

/** Validate a version-1 event. Optional context enforces current-session and branch uniqueness rules. */
export function validateEvent(event, context = {}) {
	assertObject(event, "event");
	for (const field of BASE_FIELDS) {
		if (!Object.hasOwn(event, field)) fail(`event.${field} is required`);
	}
	if (event.schemaVersion !== SCHEMA_VERSION) fail("schemaVersion must be 1");
	if (!Object.hasOwn(EVENT_FIELDS, event.eventType)) fail("eventType is unknown");
	assertUuid(event.eventId, "eventId");
	assertSessionId(event.sessionId);

	switch (event.eventType) {
		case "invocation_started": validateStart(event); break;
		case "invocation_terminal": validateTerminal(event); break;
		case "proposal_disposition": validateDisposition(event); break;
		case "invalid_event": validateInvalidEvent(event); break;
		default: fail("eventType is unknown");
	}
	validateContext(event, context);
	return event;
}

function dependencyUuid(uuid) {
	const value = typeof uuid === "function" ? uuid() : uuid?.next?.() ?? uuid?.uuid?.();
	assertUuid(value, "generated event ID");
	return value;
}

function dependencyTime(clock) {
	let value;
	if (typeof clock === "function") value = clock();
	else if (typeof clock?.iso === "function") value = clock.iso();
	else if (typeof clock?.now === "function") value = clock.now();
	if (value instanceof Date) value = value.toISOString();
	assertTimestamp(value, "generated timestamp");
	return value;
}

function deepFreeze(value) {
	if (value && typeof value === "object" && !Object.isFrozen(value)) {
		Object.freeze(value);
		for (const child of Object.values(value)) deepFreeze(child);
	}
	return value;
}

function checked(event, context) {
	validateEvent(event, context);
	return deepFreeze(event);
}

export function createInvocationStart(
	{ sessionId, skillId, candidateIds } = {},
	{ clock, uuid, eventIds, invocationIds } = {},
) {
	assertSessionId(sessionId);
	assertEnum(skillId, APPROVED_SKILL_IDS, "skillId");
	assertCandidateIds(candidateIds);
	const event = {
		schemaVersion: SCHEMA_VERSION,
		eventType: "invocation_started",
		eventId: dependencyUuid(uuid),
		invocationId: dependencyUuid(uuid),
		sessionId,
		skillId,
		startedAt: dependencyTime(clock),
		candidateIds: [...candidateIds],
	};
	return checked(event, { sessionId, eventIds, invocationIds });
}

function normalizeProposal(proposal, invocationId) {
	assertObject(proposal, "proposal");
	assertExactFields(proposal, PROPOSAL_FIELDS, ["candidateId", "rank", "score"], "proposal");
	const normalized = {
		proposalId: `${invocationId}:proposal:${proposal.candidateId}`,
		candidateId: proposal.candidateId,
		rank: proposal.rank,
		score: proposal.score,
	};
	if (Object.hasOwn(proposal, "proposalId") && proposal.proposalId !== normalized.proposalId) {
		fail("proposal.proposalId must use invocationId:proposal:candidateId");
	}
	if (Object.hasOwn(proposal, "confidence")) normalized.confidence = proposal.confidence;
	return normalized;
}

export function createInvocationTerminal(
	{ start, sessionId = start?.sessionId, status, failureClass, proposals = [] } = {},
	{ clock, uuid, eventIds, existingTerminal } = {},
) {
	validateEvent(start, { sessionId });
	if (start.eventType !== "invocation_started") fail("start must be an InvocationStart");
	if (existingTerminal !== undefined) fail("duplicate_terminal: invocation already has a terminal", "duplicate_terminal");
	const event = {
		schemaVersion: SCHEMA_VERSION,
		eventType: "invocation_terminal",
		eventId: dependencyUuid(uuid),
		invocationId: start.invocationId,
		sessionId,
		finishedAt: dependencyTime(clock),
		status,
	};
	if (status !== "succeeded" && failureClass !== undefined) event.failureClass = failureClass;
	if (!Array.isArray(proposals)) fail("proposals must be an array");
	event.proposals = proposals.map((proposal) => normalizeProposal(proposal, start.invocationId));
	return checked(event, { sessionId, start, eventIds });
}

export function createDisposition(
	{ proposalId, sessionId, skillId, disposition } = {},
	{ clock, uuid, proposal, start, terminal, existingDisposition, eventIds } = {},
) {
	validateEvent(start, { sessionId: start?.sessionId });
	if (start.eventType !== "invocation_started") fail("start must be an InvocationStart");
	let terminalIsSuccessful = false;
	try {
		validateEvent(terminal, { sessionId: start.sessionId, start });
		terminalIsSuccessful = terminal.eventType === "invocation_terminal" && terminal.status === "succeeded";
	} catch {
		terminalIsSuccessful = false;
	}
	if (!terminalIsSuccessful || !isObject(proposal) || proposal.proposalId !== proposalId ||
		proposal.proposalId !== `${start.invocationId}:proposal:${proposal.candidateId}` ||
		!terminal.proposals.some(({ proposalId: id }) => id === proposalId) ||
		!start.candidateIds.includes(proposal.candidateId)) {
		fail("unknown_proposal: proposal must reference a successful proposal", "unknown_proposal");
	}
	if (sessionId !== start.sessionId) fail("cross_session: sessionId must match proposal/current session", "cross_session");
	if (skillId !== start.skillId) fail("skillId must match the proposal invocation");
	assertEnum(disposition, DISPOSITIONS, "disposition");

	if (existingDisposition !== undefined) {
		validateEvent(existingDisposition, { sessionId });
		if (existingDisposition.eventType !== "proposal_disposition" ||
			existingDisposition.proposalId !== proposalId || existingDisposition.skillId !== start.skillId) {
			fail("existingDisposition must validly reference the same proposal and skill");
		}
		if (existingDisposition.disposition !== disposition) {
			fail("conflicting_disposition: a different disposition was already recorded", "conflicting_disposition");
		}
		return Object.freeze({ event: existingDisposition, idempotentReplay: true });
	}

	const event = checked({
		schemaVersion: SCHEMA_VERSION,
		eventType: "proposal_disposition",
		eventId: dependencyUuid(uuid),
		proposalId,
		sessionId,
		skillId,
		disposition,
		recordedAt: dependencyTime(clock),
	}, { sessionId, eventIds });
	return Object.freeze({ event, idempotentReplay: false });
}

export function createInvalidEvent(
	{ sessionId, operation, reason } = {},
	{ clock, uuid, eventIds } = {},
) {
	return checked({
		schemaVersion: SCHEMA_VERSION,
		eventType: "invalid_event",
		eventId: dependencyUuid(uuid),
		sessionId,
		operation,
		reason,
		recordedAt: dependencyTime(clock),
	}, { sessionId, eventIds });
}
