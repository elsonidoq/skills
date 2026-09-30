import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
	EXIT_FAILURES,
	SCORE_LEVELS,
	buildJevRequest,
	normalizeJevResponse,
	runJevRanking,
} from "../lib/jev-client.js";
import { createFakeClock, createFakeProcessAdapter, createUuidSource } from "./helpers.js";

const fixture = JSON.parse(
	await readFile(new URL("../fixtures/jev-responses/cases.json", import.meta.url), "utf8"),
);
const clone = (value) => structuredClone(value);

function dependencies(plans, overrides = {}) {
	return {
		processAdapter: createFakeProcessAdapter(plans),
		clock: createFakeClock(),
		uuid: createUuidSource(),
		...overrides,
	};
}

function input(candidates = fixture.candidates) {
	return {
		sessionId: fixture.sessionId,
		skillId: fixture.skillId,
		criterion: fixture.criterion,
		candidates: clone(candidates),
	};
}

function responseFor(count) {
	return {
		answers: Object.fromEntries(Array.from({ length: count }, (_, index) => [
			`candidate_${index}`,
			{ score: count - index },
		])),
	};
}

test("builds one bounded Jev 0.6.3 batched request with one ordered score question per candidate", () => {
	const request = buildJevRequest(input());
	assert.deepEqual(request.state, {
		criterion: fixture.criterion,
		candidates: fixture.candidates,
	});
	assert.deepEqual(Object.keys(request.questions), ["candidate_0", "candidate_1", "candidate_2"]);
	for (const [index, candidate] of fixture.candidates.entries()) {
		assert.deepEqual(request.questions[`candidate_${index}`], {
			type: "score",
			instructions: `${fixture.criterion} Candidate: ${candidate.candidateId}.`,
			criteria: SCORE_LEVELS,
		});
	}
});

test("runs only configured executable with argument array run - and request JSON on stdin", async () => {
	const recordedEvents = [];
	const processAdapter = createFakeProcessAdapter([
		(call) => {
			assert.equal(recordedEvents.length, 1, "start must be recorded before process launch");
			assert.equal(recordedEvents[0].eventType, "invocation_started");
			return { code: 0, stdout: JSON.stringify(fixture.successWithTie) };
		},
	]);
	let processOptions;
	const fakeRun = processAdapter.run.bind(processAdapter);
	processAdapter.run = (command, args, options) => {
		processOptions = options;
		return fakeRun(command, args, options);
	};
	const deps = dependencies([], {
		processAdapter,
		executable: "/fixture/bin/jev",
		onEvent: async (event) => recordedEvents.push(event),
	});

	const result = await runJevRanking(input(), deps);
	assert.equal(deps.processAdapter.calls.length, 1);
	assert.deepEqual(deps.processAdapter.calls[0].args, ["run", "-"]);
	assert.equal(deps.processAdapter.calls[0].command, "/fixture/bin/jev");
	assert.equal(processOptions.shell, false);
	assert.deepEqual(JSON.parse(deps.processAdapter.calls[0].input), buildJevRequest(input()));
	assert.equal(recordedEvents.length, 2);
	assert.strictEqual(recordedEvents[0], result.start);
	assert.strictEqual(recordedEvents[1], result.terminal);
});

test("normalizes complete answers into stable descending ranks with original-order tie breaks", async () => {
	const deps = dependencies([{ code: 0, stdout: JSON.stringify(fixture.successWithTie) }]);
	const { start, terminal } = await runJevRanking(input(), deps);
	assert.equal(terminal.status, "succeeded");
	assert.equal("failureClass" in terminal, false);
	assert.deepEqual(terminal.proposals.map(({ candidateId, rank, score }) => ({ candidateId, rank, score })), [
		{ candidateId: "review-b", rank: 1, score: 9 },
		{ candidateId: "review-a", rank: 2, score: 7 },
		{ candidateId: "review-c", rank: 3, score: 7 },
	]);
	assert.equal(terminal.proposals[0].proposalId, `${start.invocationId}:proposal:review-b`);
	assert.equal("confidence" in terminal.proposals[0], false);
	assert.equal(terminal.proposals[1].confidence, 0.8);
	assert.equal(terminal.proposals[2].confidence, 0.5);
});

test("accepts exactly the lower and upper candidate bounds of 2 and 50", async () => {
	for (const count of fixture.candidateBounds) {
		const candidates = Array.from({ length: count }, (_, index) => ({
			candidateId: `candidate-${String(index + 1).padStart(2, "0")}`,
			body: `synthetic body ${index + 1}`,
		}));
		const deps = dependencies([{ code: 0, stdout: JSON.stringify(responseFor(count)) }]);
		const result = await runJevRanking(input(candidates), deps);
		assert.equal(result.terminal.status, "succeeded");
		assert.equal(result.terminal.proposals.length, count);
		assert.equal(deps.processAdapter.calls.length, 1);
	}
});

test("rejects candidate sets of 1 and 51 before recording or launching", async () => {
	for (const count of fixture.rejectedCandidateCounts) {
		const candidates = Array.from({ length: count }, (_, index) => ({
			candidateId: `c${index}`,
			body: `body ${index}`,
		}));
		const events = [];
		const deps = dependencies([], { onEvent: async (event) => events.push(event) });
		await assert.rejects(() => runJevRanking(input(candidates), deps), (error) => error?.reason === "input");
		assert.equal(deps.processAdapter.calls.length, 0);
		assert.deepEqual(events, []);
	}
});

test("rejects malformed request fields before launching", async () => {
	for (const invalid of [
		{ ...input(), criterion: "" },
		{ ...input(), candidates: [{ candidateId: "ok-1", body: "a" }, { candidateId: "ok-2", body: 2 }] },
		{ ...input(), candidates: [{ candidateId: "same", body: "a" }, { candidateId: "same", body: "b" }] },
	]) {
		const deps = dependencies([]);
		await assert.rejects(() => runJevRanking(invalid, deps), (error) => error?.reason === "input");
		assert.equal(deps.processAdapter.calls.length, 0);
	}
});

test("maps CLI absence to unavailable/cli_missing without retaining the process error", async () => {
	const missing = new Error("spawn /private/path/jev ENOENT");
	missing.code = "ENOENT";
	const result = await runJevRanking(input(), dependencies([missing]));
	assert.equal(result.terminal.status, "unavailable");
	assert.equal(result.terminal.failureClass, "cli_missing");
	assert.deepEqual(result.terminal.proposals, []);
	assert.equal(JSON.stringify(result).includes("/private/path"), false);
});

test("maps Jev exit codes 1 through 4 to stable terminal status and failure classes", async () => {
	assert.deepEqual(EXIT_FAILURES, {
		1: { status: "failed", failureClass: "provider" },
		2: { status: "failed", failureClass: "input" },
		3: { status: "unavailable", failureClass: "auth" },
		4: { status: "failed", failureClass: "retryable" },
	});
	for (const exitCase of fixture.exitCases) {
		const deps = dependencies([{ code: exitCase.code, stderr: fixture.stderrSentinel }]);
		const result = await runJevRanking(input(), deps);
		assert.equal(result.terminal.status, exitCase.status);
		assert.equal(result.terminal.failureClass, exitCase.failureClass);
		assert.deepEqual(result.terminal.proposals, []);
		assert.equal(JSON.stringify(result).includes(fixture.stderrSentinel), false);
	}
});

test("maps cancellation to failed/cancelled and persists no cancellation text", async () => {
	const result = await runJevRanking(input(), dependencies([{ cancelled: true }]));
	assert.equal(result.terminal.status, "failed");
	assert.equal(result.terminal.failureClass, "cancelled");
	assert.deepEqual(result.terminal.proposals, []);
	assert.equal(JSON.stringify(result).includes("cancelled"), true, "stable class is retained");
	assert.equal(JSON.stringify(result).includes("fake process"), false, "raw cancellation error is excluded");
});

test("maps malformed JSON, missing, extra, and type-invalid answers to malformed/response_schema", async () => {
	const outputs = [fixture.malformedJson, ...fixture.invalidResponses.map(({ value }) => JSON.stringify(value))];
	for (const stdout of outputs) {
		const result = await runJevRanking(input(), dependencies([{ code: 0, stdout }]));
		assert.equal(result.terminal.status, "malformed");
		assert.equal(result.terminal.failureClass, "response_schema");
		assert.deepEqual(result.terminal.proposals, []);
		assert.equal(JSON.stringify(result).includes(stdout), false, "raw response must not be retained");
	}
});

test("response normalizer requires exactly one finite score answer per candidate", () => {
	assert.deepEqual(normalizeJevResponse(fixture.successWithTie, fixture.candidates), [
		{ candidateId: "review-b", rank: 1, score: 9 },
		{ candidateId: "review-a", rank: 2, score: 7, confidence: 0.8 },
		{ candidateId: "review-c", rank: 3, score: 7, confidence: 0.5 },
	]);
	for (const { value } of fixture.invalidResponses) {
		assert.throws(() => normalizeJevResponse(value, fixture.candidates));
	}
});

test("candidate bodies and criterion travel only in process stdin, never in emitted events", async () => {
	const events = [];
	const deps = dependencies([{ code: 1, stderr: fixture.stderrSentinel }], {
		onEvent: async (event) => events.push(event),
	});
	await runJevRanking(input(), deps);
	const stdin = deps.processAdapter.calls[0].input;
	assert.ok(stdin.includes(fixture.criterion));
	for (const candidate of fixture.candidates) assert.ok(stdin.includes(candidate.body));
	const telemetry = JSON.stringify(events);
	assert.equal(telemetry.includes(fixture.criterion), false);
	assert.equal(telemetry.includes(fixture.stderrSentinel), false);
	for (const candidate of fixture.candidates) assert.equal(telemetry.includes(candidate.body), false);
});
