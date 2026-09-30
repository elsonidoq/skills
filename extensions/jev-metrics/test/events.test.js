import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
	APPROVED_SKILL_IDS,
	DISPOSITIONS,
	FAILURE_CLASSES,
	INVALID_OPERATIONS,
	INVALID_REASONS,
	TERMINAL_STATUSES,
	createDisposition,
	createInvalidEvent,
	createInvocationStart,
	createInvocationTerminal,
	validateEvent,
} from "../lib/events.js";
import { createFakeClock, createUuidSource } from "./helpers.js";

const fixture = JSON.parse(
	await readFile(new URL("../fixtures/events/schema-cases.json", import.meta.url), "utf8"),
);

const clone = (value) => structuredClone(value);
const deps = () => ({ clock: createFakeClock({ start: fixture.startedAt }), uuid: createUuidSource() });

function assertInvalid(event, pattern = /invalid|required|must|unknown|unexpected/i) {
	assert.throws(() => validateEvent(event), pattern);
}

function makeStart(overrides = {}) {
	return { ...clone(fixture.validStart), ...overrides };
}

function makeTerminal(overrides = {}) {
	return { ...clone(fixture.validSuccessTerminal), ...overrides };
}

test("exports exactly the contract enumerations", () => {
	assert.deepEqual(APPROVED_SKILL_IDS, fixture.approvedSkillIds);
	assert.deepEqual(TERMINAL_STATUSES, fixture.terminalStatuses);
	assert.deepEqual(FAILURE_CLASSES, fixture.failureClasses);
	assert.deepEqual(DISPOSITIONS, fixture.dispositions);
	assert.deepEqual(INVALID_OPERATIONS, fixture.invalidOperations);
	assert.deepEqual(INVALID_REASONS, fixture.invalidReasons);
});

test("InvocationStart uses generated identifiers/time and preserves opaque candidate ID order", () => {
	const { clock, uuid } = deps();
	const event = createInvocationStart(
		{
			sessionId: fixture.sessionId,
			skillId: "receiving-code-review",
			candidateIds: fixture.candidateIds,
		},
		{ clock, uuid },
	);

	assert.deepEqual(event, {
		schemaVersion: 1,
		eventType: "invocation_started",
		eventId: "00000000-0000-4000-8000-000000000001",
		invocationId: "00000000-0000-4000-8000-000000000002",
		sessionId: fixture.sessionId,
		skillId: "receiving-code-review",
		startedAt: fixture.startedAt,
		candidateIds: fixture.candidateIds,
	});
	assert.notStrictEqual(event.candidateIds, fixture.candidateIds);
	assert.equal(validateEvent(event), event);
});

test("InvocationStart requires schema/base fields, approved skill, session, unique bounded candidate IDs", () => {
	for (const field of ["schemaVersion", "eventType", "eventId", "invocationId", "sessionId", "skillId", "startedAt", "candidateIds"]) {
		const event = makeStart();
		delete event[field];
		assertInvalid(event);
	}
	for (const skillId of fixture.approvedSkillIds) {
		assert.equal(validateEvent(makeStart({ skillId })).skillId, skillId);
	}
	assertInvalid(makeStart({ schemaVersion: 2 }), /schemaVersion/i);
	assertInvalid(makeStart({ skillId: "finish-session" }), /skillId/i);
	assertInvalid(makeStart({ sessionId: "" }), /sessionId/i);
	assertInvalid(makeStart({ candidateIds: ["only-one"] }), /candidateIds/i);
	assert.equal(validateEvent(makeStart({ candidateIds: fixture.fiftyCandidateIds })).candidateIds.length, 50);
	assertInvalid(makeStart({ candidateIds: [...fixture.fiftyCandidateIds, "c51"] }), /candidateIds/i);
	assertInvalid(makeStart({ candidateIds: ["candidate-1", "candidate-1"] }), /candidateIds/i);
	for (const candidateId of fixture.malformedCandidateIds) {
		assertInvalid(makeStart({ candidateIds: ["valid", candidateId] }), /candidateId/i);
	}
	assert.throws(() => validateEvent(fixture.validStart, { sessionId: fixture.otherSessionId }), /sessionId/i);
	assert.throws(() => validateEvent(fixture.validStart, { eventIds: new Set([fixture.validStart.eventId]) }), /eventId/i);
	assert.throws(() => validateEvent(fixture.validStart, { invocationIds: new Set([fixture.validStart.invocationId]) }), /invocationId/i);
});

test("InvocationTerminal enforces reference-time, status/failure, and complete proposal invariants", () => {
	assert.equal(validateEvent(fixture.validSuccessTerminal).status, "succeeded");
	for (const status of fixture.terminalStatuses) {
		const event = status === "succeeded"
			? makeTerminal()
			: makeTerminal({ status, failureClass: fixture.failureClasses[0], proposals: [] });
		assert.equal(validateEvent(event).status, status);
	}
	for (const failureClass of fixture.failureClasses) {
		assert.equal(validateEvent(makeTerminal({ status: "failed", failureClass, proposals: [] })).failureClass, failureClass);
	}
	assertInvalid(makeTerminal({ failureClass: "provider" }), /failureClass/i);
	const failedWithoutClass = makeTerminal({ status: "failed", proposals: [] });
	assert.equal(validateEvent(failedWithoutClass), failedWithoutClass);
	assert.equal(Object.hasOwn(failedWithoutClass, "failureClass"), false);
	assertInvalid(makeTerminal({ status: "failed", failureClass: "stderr details", proposals: [] }), /failureClass/i);
	assertInvalid(makeTerminal({ status: "failed", failureClass: "provider", proposals: [fixture.validSuccessTerminal.proposals[0]] }), /proposals/i);
	assertInvalid(makeTerminal({ status: "succeeded", proposals: [] }), /proposals/i);
	assert.throws(() => validateEvent(fixture.validSuccessTerminal, { sessionId: fixture.sessionId, start: makeStart({ invocationId: "00000000-0000-4000-8000-000000000199" }) }), /invocationId/i);
	assert.throws(() => validateEvent(fixture.validSuccessTerminal, { sessionId: fixture.otherSessionId, start: fixture.validStart }), /sessionId/i);
});

test("successful terminal construction requires one stable proposal per start candidate", () => {
	const start = fixture.validStart;
	const { clock, uuid } = deps();
	clock.set(fixture.finishedAt);
	const terminal = createInvocationTerminal(
		{
			start,
			status: "succeeded",
			proposals: [
				{ candidateId: "candidate-1", rank: 2, score: 4 },
				{ candidateId: "candidate_2", rank: 1, score: 8, confidence: 0.75 },
				{ candidateId: "C.3:part", rank: 3, score: -2 },
			],
		},
		{ clock, uuid },
	);

	assert.equal(terminal.invocationId, start.invocationId);
	assert.deepEqual(terminal.proposals.map(({ proposalId }) => proposalId), start.candidateIds.map(
		(candidateId) => `${start.invocationId}:proposal:${candidateId}`,
	));
	assert.deepEqual(terminal.proposals.map(({ rank }) => rank), [2, 1, 3]);
	assert.equal("confidence" in terminal.proposals[0], false);
	assert.equal(terminal.proposals[1].confidence, 0.75);
	assert.equal("failureClass" in terminal, false);

	for (const proposals of [
		terminal.proposals.slice(0, 2),
		[...terminal.proposals, terminal.proposals[0]],
		terminal.proposals.map((proposal, index) => ({ ...proposal, rank: index === 0 ? 1 : proposal.rank })),
		terminal.proposals.map((proposal, index) => ({ ...proposal, score: index === 0 ? Infinity : proposal.score })),
		terminal.proposals.map((proposal, index) => ({ ...proposal, confidence: index === 0 ? Number.NaN : proposal.confidence })),
	]) {
		assert.throws(() => createInvocationTerminal({ start, status: "succeeded", proposals }, deps()));
	}
	assert.throws(() => createInvocationTerminal({ start, status: "succeeded", proposals: terminal.proposals.map((p, i) => i === 0 ? { ...p, candidateId: "unknown" } : p) }, deps()));
});

test("terminal construction requires current matching session and finish not before start", () => {
	const { clock, uuid } = deps();
	clock.set("2025-12-31T23:59:59.000Z");
	assert.throws(() => createInvocationTerminal({ start: fixture.validStart, status: "failed", failureClass: "provider", proposals: [] }, { clock, uuid }), /finishedAt/i);
	assert.throws(() => createInvocationTerminal({ start: fixture.validStart, sessionId: fixture.otherSessionId, status: "failed", failureClass: "provider", proposals: [] }, deps()), /sessionId/i);
});

test("Disposition validates proposal/session/skill references and first-valid-write semantics", () => {
	const context = {
		proposal: fixture.validSuccessTerminal.proposals[0],
		start: fixture.validStart,
		terminal: fixture.validSuccessTerminal,
	};
	const first = createDisposition(
		{ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition: "accepted" },
		{ ...deps(), ...context },
	);
	assert.equal(first.idempotentReplay, false);
	assert.equal(first.event.eventType, "proposal_disposition");
	assert.equal(first.event.recordedAt, fixture.startedAt);

	const replay = createDisposition(
		{ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition: "accepted" },
		{ ...deps(), ...context, existingDisposition: first.event },
	);
	assert.deepEqual(replay, { event: first.event, idempotentReplay: true });
	assert.throws(() => createDisposition(
		{ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition: "overridden" },
		{ ...deps(), ...context, existingDisposition: first.event },
	), /conflicting_disposition/i);
	assert.throws(() => createDisposition({ proposalId: "unknown", sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition: "accepted" }, { ...deps(), ...context }), /unknown_proposal/i);
	assert.throws(() => createDisposition({ proposalId: context.proposal.proposalId, sessionId: fixture.otherSessionId, skillId: fixture.validStart.skillId, disposition: "accepted" }, { ...deps(), ...context }), /cross_session/i);
	assert.throws(() => createDisposition({ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: "speckit-tasks", disposition: "accepted" }, { ...deps(), ...context }), /skillId/i);
	for (const disposition of fixture.dispositions) {
		assert.equal(createDisposition(
			{ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition },
			{ ...deps(), ...context },
		).event.disposition, disposition);
	}
	assert.throws(() => createDisposition(
		{ proposalId: context.proposal.proposalId, sessionId: fixture.sessionId, skillId: fixture.validStart.skillId, disposition: "accepted" },
		{ ...deps(), ...context, terminal: { ...fixture.validSuccessTerminal, status: "failed", failureClass: "provider", proposals: [] } },
	), /unknown_proposal/i);
});

test("InvalidEvent uses only stable operations/reasons and generated identity/time", () => {
	for (const operation of fixture.invalidOperations) {
		for (const reason of fixture.invalidReasons) {
			const event = createInvalidEvent({ sessionId: fixture.sessionId, operation, reason }, deps());
			assert.equal(validateEvent(event), event);
			assert.deepEqual(Object.keys(event), ["schemaVersion", "eventType", "eventId", "sessionId", "operation", "reason", "recordedAt"]);
		}
	}
	assert.throws(() => createInvalidEvent({ sessionId: fixture.sessionId, operation: "network", reason: "schema_invalid" }, deps()));
	assert.throws(() => createInvalidEvent({ sessionId: fixture.sessionId, operation: "rank", reason: "raw error text" }, deps()));
});

test("every event variant requires current session, unique event ID, and its complete allowlisted field set", () => {
	for (const [source, fields] of [
		[fixture.validSuccessTerminal, ["schemaVersion", "eventType", "eventId", "invocationId", "sessionId", "finishedAt", "status", "proposals"]],
		[fixture.validDisposition, ["schemaVersion", "eventType", "eventId", "proposalId", "sessionId", "skillId", "disposition", "recordedAt"]],
		[fixture.validInvalidEvent, ["schemaVersion", "eventType", "eventId", "sessionId", "operation", "reason", "recordedAt"]],
	]) {
		assert.throws(() => validateEvent(source, { sessionId: fixture.otherSessionId }), /sessionId/i);
		assert.throws(() => validateEvent(source, { eventIds: new Set([source.eventId]) }), /eventId/i);
		for (const field of fields) {
			const event = clone(source);
			delete event[field];
			assertInvalid(event);
		}
	}
});

test("structural validation rejects malformed identifiers, unknown schema/event, and additional fields", () => {
	assertInvalid(makeStart({ eventId: "not-a-uuid" }), /eventId/i);
	assertInvalid(makeStart({ invocationId: "not-a-uuid" }), /invocationId/i);
	assertInvalid(makeStart({ startedAt: "not-a-date" }), /startedAt/i);
	assertInvalid({ ...fixture.validStart, eventType: "unknown" }, /eventType/i);
	assertInvalid({ ...fixture.validStart, schemaVersion: 99 }, /schemaVersion/i);
	for (const field of fixture.forbiddenFieldNames) {
		assertInvalid({ ...fixture.validStart, [field]: "PRIVATE_SENTINEL" }, /unexpected/i);
		assertInvalid({ ...fixture.validSuccessTerminal, [field]: "PRIVATE_SENTINEL" }, /unexpected/i);
		assertInvalid({ ...fixture.validDisposition, [field]: "PRIVATE_SENTINEL" }, /unexpected/i);
		assertInvalid({ ...fixture.validInvalidEvent, [field]: "PRIVATE_SENTINEL" }, /unexpected/i);
	}
});

test("constructed telemetry contains no candidate bodies, logs, prompts, credentials, personal data, responses, stderr, endpoints, or provider payloads", () => {
	const start = createInvocationStart({ sessionId: fixture.sessionId, skillId: fixture.approvedSkillIds[0], candidateIds: ["opaque-1", "opaque-2"] }, deps());
	const serialized = JSON.stringify(start);
	for (const sentinel of fixture.privacySentinels) assert.equal(serialized.includes(sentinel), false);
	for (const field of fixture.forbiddenFieldNames) assert.equal(Object.hasOwn(start, field), false);
});
