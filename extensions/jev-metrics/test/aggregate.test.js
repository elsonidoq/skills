import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { CUSTOM_ENTRY_TYPE, aggregateActiveBranch, aggregateEvents } from "../lib/aggregate.js";

const fixture = JSON.parse(
	await readFile(new URL("../fixtures/events/aggregate-cases.json", import.meta.url), "utf8"),
);
const clone = (value) => structuredClone(value);
const options = { sessionId: fixture.sessionId, leafId: fixture.leafId };

function entry(data, id) {
	return {
		id: id ?? `entry-${data.eventId}`,
		type: "custom",
		customType: fixture.customType,
		data: clone(data),
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

function assertArithmetic(summary) {
	assert.ok(summary.successes <= summary.attempts);
	assert.equal(summary.accepted + summary.overridden + summary.notUsed + summary.pending, summary.proposals);
}

test("aggregates the exact success fixture before dispositions with required summary fields", () => {
	assert.equal(CUSTOM_ENTRY_TYPE, fixture.customType);
	const result = aggregateActiveBranch(
		[entry(fixture.events.start), entry(fixture.events.terminal)],
		{ ...options, customType: fixture.customType },
	);
	assert.equal(result.sessionId, fixture.sessionId);
	assert.equal(result.leafId, fixture.leafId);
	assert.equal(result.eventState, "available");
	assert.deepEqual(counters(result.total), {
		attempts: 1,
		successes: 1,
		proposals: 3,
		accepted: 0,
		overridden: 0,
		notUsed: 0,
		pending: 3,
		invalidEvents: 0,
	});
	assert.equal(result.total.sessionId, fixture.sessionId);
	assert.equal(result.total.leafId, fixture.leafId);
	assert.equal(result.total.scope, "session");
	assert.equal(result.total.coverage, "instrumented-only");
	assert.deepEqual(result.bySkill.map(({ scope }) => scope), ["receiving-code-review"]);
	assert.deepEqual(counters(result.bySkill[0]), counters(result.total));
	assert.equal(Object.hasOwn(result.total, "storeState"), false, "storeState is history-only");
	assertArithmetic(result.total);
});

test("counts exactly two accepted, one overridden, zero not-used, zero pending after dispositions", () => {
	const events = [
		fixture.events.start,
		fixture.events.terminal,
		fixture.events.accepted1,
		fixture.events.accepted2,
		fixture.events.overridden,
	];
	const result = aggregateEvents(events, options);
	assert.deepEqual(counters(result.total), {
		attempts: 1,
		successes: 1,
		proposals: 3,
		accepted: 2,
		overridden: 1,
		notUsed: 0,
		pending: 0,
		invalidEvents: 0,
	});
	assertArithmetic(result.total);
});

test("event replay and duplicate event IDs cannot inflate any counter", () => {
	const events = [
		fixture.events.start,
		fixture.events.terminal,
		fixture.events.accepted1,
		fixture.events.accepted2,
		fixture.events.overridden,
	];
	const baseline = aggregateEvents(events, options);
	const replayed = aggregateEvents([...events, ...events, clone(fixture.events.accepted1)], options);
	assert.deepEqual(replayed.total, baseline.total);
	assert.deepEqual(replayed.bySkill, baseline.bySkill);
	assertArithmetic(replayed.total);
});

test("first valid disposition wins and a conflicting later write is explicit and ignored", () => {
	const acceptedFirst = aggregateEvents([
		fixture.events.start,
		fixture.events.terminal,
		fixture.events.accepted1,
		fixture.events.conflict,
	], options);
	assert.deepEqual(
		{ accepted: acceptedFirst.total.accepted, overridden: acceptedFirst.total.overridden, notUsed: acceptedFirst.total.notUsed, pending: acceptedFirst.total.pending },
		{ accepted: 1, overridden: 0, notUsed: 0, pending: 2 },
	);
	assert.ok(acceptedFirst.issues.some(({ reason }) => reason === "conflicting_disposition"));

	const notUsedFirst = aggregateEvents([
		fixture.events.start,
		fixture.events.terminal,
		fixture.events.conflict,
		fixture.events.accepted1,
	], options);
	assert.deepEqual(
		{ accepted: notUsedFirst.total.accepted, overridden: notUsedFirst.total.overridden, notUsed: notUsedFirst.total.notUsed, pending: notUsedFirst.total.pending },
		{ accepted: 0, overridden: 0, notUsed: 1, pending: 2 },
	);
	assertArithmetic(acceptedFirst.total);
	assertArithmetic(notUsedFirst.total);
});

test("orphan starts remain attempts with an explicit incomplete state", () => {
	const result = aggregateEvents([fixture.events.orphanStart], options);
	assert.deepEqual(counters(result.total), {
		attempts: 1,
		successes: 0,
		proposals: 0,
		accepted: 0,
		overridden: 0,
		notUsed: 0,
		pending: 0,
		invalidEvents: 0,
	});
	assert.equal(result.eventState, "orphaned");
	assert.ok(result.issues.some(({ reason }) => reason === "orphan_start"));
	assertArithmetic(result.total);
});

test("active-branch input excludes abandoned branch events", () => {
	const activeBranch = [entry(fixture.events.start), entry(fixture.events.terminal)];
	const abandonedBranch = [entry(fixture.events.abandonedStart)];
	const active = aggregateActiveBranch(activeBranch, { ...options, customType: fixture.customType });
	assert.equal(active.total.attempts, 1);
	assert.deepEqual(active.bySkill.map(({ scope }) => scope), ["receiving-code-review"]);
	assert.equal(active.bySkill.some(({ scope }) => scope === "scientific-method-debugging"), false);
	assert.equal(aggregateActiveBranch(abandonedBranch, { ...options, customType: fixture.customType }).total.attempts, 1);
});

test("validated InvalidEvent entries are counted once but invalid diagnostics are not", () => {
	const result = aggregateEvents([
		fixture.events.start,
		fixture.events.terminal,
		fixture.events.invalidDiagnostic,
		fixture.events.invalidDiagnostic,
		{ ...fixture.events.invalidDiagnostic, eventId: "not-a-uuid" },
	], options);
	assert.equal(result.total.invalidEvents, 1);
	assert.equal(result.eventState, "corrupt");
	assertArithmetic(result.total);
});

test("duplicate terminals, unknown proposals, and cross-session events never inflate counts", () => {
	const duplicateTerminal = {
		...clone(fixture.events.terminal),
		eventId: "10000000-0000-4000-8000-000000000099",
		status: "failed",
		failureClass: "provider",
		proposals: [],
	};
	const unknownDisposition = {
		...clone(fixture.events.accepted1),
		eventId: "10000000-0000-4000-8000-000000000098",
		proposalId: "10000000-0000-4000-8000-000000000101:proposal:missing",
	};
	const result = aggregateEvents([
		fixture.events.start,
		fixture.events.terminal,
		duplicateTerminal,
		unknownDisposition,
		fixture.events.crossSessionStart,
	], options);
	assert.deepEqual(counters(result.total), {
		attempts: 1,
		successes: 1,
		proposals: 3,
		accepted: 0,
		overridden: 0,
		notUsed: 0,
		pending: 3,
		invalidEvents: 0,
	});
	assert.ok(result.issues.some(({ reason }) => reason === "duplicate_terminal"));
	assert.ok(result.issues.some(({ reason }) => reason === "unknown_proposal"));
	assert.ok(result.issues.some(({ reason }) => reason === "cross_session"));
	assertArithmetic(result.total);
});

test("unsupported and corrupt active histories are explicit rather than available fabricated zeroes", () => {
	const unsupported = aggregateActiveBranch([entry(fixture.unsupportedEvent)], { ...options, customType: fixture.customType });
	assert.equal(unsupported.eventState, "unsupported");
	assert.equal(unsupported.total.attempts, 0);
	assert.ok(unsupported.issues.some(({ reason }) => reason === "unsupported_schema"));

	const corrupt = aggregateActiveBranch([entry(fixture.corruptEvent)], { ...options, customType: fixture.customType });
	assert.equal(corrupt.eventState, "corrupt");
	assert.equal(corrupt.total.attempts, 0);
	assert.ok(corrupt.issues.some(({ reason }) => reason === "corrupt_event"));
});

test("non-owned, non-custom, and unwrapped branch entries do not enter telemetry", () => {
	const result = aggregateActiveBranch([
		{ type: "message", data: fixture.events.start },
		{ type: "custom", customType: "other-extension", data: fixture.events.start },
		fixture.events.start,
	], { ...options, customType: fixture.customType });
	assert.equal(result.eventState, "available");
	assert.equal(result.total.attempts, 0);
	assert.deepEqual(result.bySkill, []);
});
