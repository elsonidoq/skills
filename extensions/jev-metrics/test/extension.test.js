import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { getStorePath } from "../lib/csv-store.js";
import { CUSTOM_ENTRY_TYPE } from "../lib/aggregate.js";
import { createJevMetricsExtension } from "../index.js";
import {
	FakeExtensionAPI,
	FakeSessionManager,
	createFakeClock,
	createFakeExtensionContext,
	createFakeProcessAdapter,
	createFilesystemFixture,
	createUuidSource,
} from "./helpers.js";

const responses = JSON.parse(
	await readFile(new URL("../fixtures/jev-responses/cases.json", import.meta.url), "utf8"),
);

function rankInput() {
	return {
		skillId: responses.skillId,
		criterion: responses.criterion,
		candidates: structuredClone(responses.candidates),
	};
}

function setup({ plans = [], sessionManager, filesystem, overrides = {} } = {}) {
	const manager = sessionManager ?? new FakeSessionManager();
	const context = createFakeExtensionContext({ sessionManager: manager, cwd: manager.getCwd() });
	const api = new FakeExtensionAPI({ context });
	const processAdapter = createFakeProcessAdapter(plans);
	const extension = createJevMetricsExtension({
		processAdapter,
		clock: createFakeClock(),
		uuid: createUuidSource(),
		stateHome: filesystem?.path("state"),
		...overrides,
	});
	extension(api);
	return { api, context, manager, processAdapter };
}

function details(result) {
	assert.equal(result.content.length, 1);
	assert.equal(result.content[0].type, "text");
	assert.deepEqual(JSON.parse(result.content[0].text), result.details);
	return result.details;
}

test("registers exactly three model-callable tools and /jev-metrics", () => {
	const { api } = setup();
	assert.deepEqual([...api.tools.keys()], ["jev_rank", "jev_disposition", "jev_metrics"]);
	assert.deepEqual([...api.commands.keys()], ["jev-metrics"]);
	for (const tool of api.tools.values()) {
		assert.equal(typeof tool.description, "string");
		assert.equal(typeof tool.parameters, "object");
		assert.equal(typeof tool.execute, "function");
	}
});

test("appends invocation start before launch and terminal after a successful fake process", async () => {
	let manager;
	const plan = () => {
		const events = manager.getBranch().map(({ data }) => data);
		assert.deepEqual(events.map(({ eventType }) => eventType), ["invocation_started"]);
		return { code: 0, stdout: JSON.stringify(responses.successWithTie) };
	};
	const setupResult = setup({ plans: [plan] });
	manager = setupResult.manager;
	const result = details(await setupResult.api.invokeTool("jev_rank", rankInput()));
	assert.equal(result.tracked, true);
	assert.equal(result.status, "succeeded");
	assert.equal(result.proposals.length, 3);
	assert.equal(result.coverage, "instrumented-only");
	assert.match(result.requiredNextAction, /disposition/i);
	assert.deepEqual(manager.getBranch().map(({ data }) => data.eventType), [
		"invocation_started",
		"invocation_terminal",
	]);
});

test("current metrics show exact denominators, active identifiers, and coverage boundary", async () => {
	const { api, manager } = setup({ plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }] });
	await api.invokeTool("jev_rank", rankInput());
	const current = details(await api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.sessionId, manager.getSessionId());
	assert.equal(current.leafId, manager.getLeafId());
	assert.equal(current.coverage, "instrumented-only");
	assert.match(current.coverageNotice, /raw shell and MCP calls are untracked/i);
	assert.deepEqual(current.total, {
		attempts: 1,
		successes: 1,
		proposals: 3,
		accepted: 0,
		overridden: 0,
		notUsed: 0,
		pending: 3,
		invalidEvents: 0,
	});
});

test("disposition first-write and replay semantics append exactly once", async () => {
	const { api, manager } = setup({ plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }] });
	const rank = details(await api.invokeTool("jev_rank", rankInput()));
	const proposalId = rank.proposals[0].proposalId;
	const first = details(await api.invokeTool("jev_disposition", { proposalId, disposition: "accepted" }));
	const countAfterFirst = manager.getBranch().length;
	assert.deepEqual(first, { recorded: true, idempotentReplay: false, proposalId, disposition: "accepted" });
	const replay = details(await api.invokeTool("jev_disposition", { proposalId, disposition: "accepted" }));
	assert.deepEqual(replay, { recorded: true, idempotentReplay: true, proposalId, disposition: "accepted" });
	assert.equal(manager.getBranch().length, countAfterFirst);
	const conflict = details(await api.invokeTool("jev_disposition", { proposalId, disposition: "overridden" }));
	assert.deepEqual(conflict, { recorded: false, reason: "conflicting_disposition" });
	const current = details(await api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.total.accepted, 1);
	assert.equal(current.total.overridden, 0);
	assert.equal(current.total.invalidEvents, 1);
});

test("unknown dispositions append a privacy-safe invalid diagnostic", async () => {
	const { api, manager } = setup();
	const result = details(await api.invokeTool("jev_disposition", {
		proposalId: "00000000-0000-4000-8000-000000000999:proposal:unknown",
		disposition: "accepted",
	}));
	assert.deepEqual(result, { recorded: false, reason: "unknown_proposal" });
	assert.equal(manager.getBranch().at(-1).data.eventType, "invalid_event");
	assert.equal(manager.getBranch().at(-1).data.reason, "unknown_proposal");
});

test("serializes sibling event-producing tool calls", async () => {
	let active = 0;
	let maximumActive = 0;
	const plan = async () => {
		active += 1;
		maximumActive = Math.max(maximumActive, active);
		await new Promise((resolve) => setTimeout(resolve, 5));
		active -= 1;
		return { code: 0, stdout: JSON.stringify(responses.successWithTie) };
	};
	const { api } = setup({ plans: [plan, plan] });
	const [first, second] = await Promise.all([
		api.invokeTool("jev_rank", rankInput()),
		api.invokeTool("jev_rank", rankInput()),
	]);
	assert.equal(details(first).status, "succeeded");
	assert.equal(details(second).status, "succeeded");
	assert.equal(maximumActive, 1);
	const current = details(await api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.total.attempts, 2);
	assert.equal(current.total.successes, 2);
});

test("session_tree reconstruction follows only the active branch and active leaf", async () => {
	const { api, manager } = setup({ plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }] });
	await api.invokeTool("jev_rank", rankInput());
	const successfulBranch = manager.getBranch();
	const successfulLeaf = manager.getLeafId();

	manager.setBranch([], { leafId: "leaf-fork-empty" });
	await api.emit("session_tree", { newLeafId: "leaf-fork-empty", oldLeafId: successfulLeaf });
	let current = details(await api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.leafId, "leaf-fork-empty");
	assert.equal(current.total.attempts, 0);

	manager.setBranch(successfulBranch, { leafId: successfulLeaf });
	await api.emit("session_tree", { newLeafId: successfulLeaf, oldLeafId: "leaf-fork-empty" });
	current = details(await api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.total.attempts, 1);
	assert.equal(current.total.successes, 1);
});

test("session_start reconstructs reload/resume state and orphan starts remain incomplete attempts", async () => {
	const manager = new FakeSessionManager();
	const firstRuntime = setup({
		sessionManager: manager,
		plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }],
	});
	await firstRuntime.api.invokeTool("jev_rank", rankInput());

	const reloaded = setup({
		sessionManager: manager,
		plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }],
	});
	await reloaded.api.emit("session_start", { reason: "resume" });
	let current = details(await reloaded.api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.total.attempts, 1);
	assert.equal(current.total.successes, 1);
	await reloaded.api.invokeTool("jev_rank", rankInput());
	current = details(await reloaded.api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.total.attempts, 2, "new writes after reload must retain unique identifiers");
	assert.equal(current.total.successes, 2);

	manager.setBranch([manager.getBranch()[0]], { leafId: "leaf-orphan" });
	await reloaded.api.emit("session_tree", { newLeafId: "leaf-orphan", oldLeafId: manager.getLeafId() });
	current = details(await reloaded.api.invokeTool("jev_metrics", { action: "current" }));
	assert.equal(current.eventState, "orphaned");
	assert.equal(current.total.attempts, 1);
	assert.equal(current.total.successes, 0);
});

test("/jev-metrics current and help render identifiers, denominators, and untracked coverage", async () => {
	const { api, manager } = setup({ plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }] });
	await api.invokeTool("jev_rank", rankInput());
	const currentText = await api.invokeCommand("jev-metrics", "");
	assert.match(currentText, new RegExp(manager.getSessionId()));
	assert.match(currentText, new RegExp(manager.getLeafId()));
	assert.match(currentText, /successes 1 \/ 1 attempts/i);
	assert.match(currentText, /accepted 0 \/ 3 proposals/i);
	assert.match(currentText, /overridden 0 \/ 3 proposals/i);
	assert.match(currentText, /not used 0 \/ 3 proposals/i);
	assert.match(currentText, /pending 3 \/ 3 proposals/i);
	assert.match(currentText, /instrumented-only/i);
	assert.match(currentText, /raw shell and MCP calls are untracked/i);

	const helpText = await api.invokeCommand("jev-metrics", "help");
	for (const term of ["attempts", "successes", "proposals", "accepted", "overridden", "not used", "pending", "invalid events"]) {
		assert.match(helpText, new RegExp(term, "i"));
	}
	assert.match(helpText, /candidate bodies.*not stored/i);
});

test("history retrieval and command expose missing and corrupt states explicitly", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const manager = new FakeSessionManager({ cwd: filesystem.root });
	const { api } = setup({ sessionManager: manager, filesystem });
	let history = details(await api.invokeTool("jev_metrics", { action: "history" }));
	assert.deepEqual(history, { storeState: "missing", coverage: "instrumented-only" });
	assert.match(await api.invokeCommand("jev-metrics", "history"), /history store: missing/i);

	const path = await getStorePath({ projectRoot: filesystem.root, stateHome: filesystem.path("state") });
	await filesystem.write(path.slice(filesystem.root.length + 1), "corrupt\n");
	history = details(await api.invokeTool("jev_metrics", { action: "history" }));
	assert.deepEqual(history, { storeState: "invalid", coverage: "instrumented-only" });
	assert.match(await api.invokeCommand("jev-metrics", "history"), /history store: invalid/i);
	const closeout = details(await api.invokeTool("jev_metrics", { action: "closeout" }));
	assert.equal(closeout.status, "store_error");
	assert.equal(closeout.storeState, "invalid");
	assert.equal(await filesystem.read(path.slice(filesystem.root.length + 1)), "corrupt\n");
});

test("closeout appends once and reports already_exported on replay", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const manager = new FakeSessionManager({ cwd: filesystem.root });
	const { api } = setup({
		sessionManager: manager,
		filesystem,
		plans: [{ code: 0, stdout: JSON.stringify(responses.successWithTie) }],
	});
	await api.invokeTool("jev_rank", rankInput());
	const first = details(await api.invokeTool("jev_metrics", { action: "closeout" }));
	assert.equal(first.status, "appended");
	assert.equal(first.sessionId, manager.getSessionId());
	assert.equal(first.total.proposals, 3);
	const second = details(await api.invokeTool("jev_metrics", { action: "closeout" }));
	assert.equal(second.status, "already_exported");
	const history = details(await api.invokeTool("jev_metrics", { action: "history" }));
	assert.equal(history.storeState, "available");
	assert.equal(history.rows.length, 1);
});

const GLOBAL_SEAM_IDS = [
	"scientific-method-debugging",
	"receiving-code-review",
	"coordinate-implementation",
	"track-open-issue",
];
const GLOBAL_SEAM_FIXTURES = await Promise.all(GLOBAL_SEAM_IDS.map(async (skillId) => ({
	skillId,
	fixture: JSON.parse(await readFile(new URL(`../fixtures/seams/${skillId}.json`, import.meta.url), "utf8")),
	skill: await readFile(new URL(`../../../skills/${skillId}/SKILL.md`, import.meta.url), "utf8"),
})));

function assertFixtureContainsOnlySafeSyntheticContent(fixture) {
	const serialized = JSON.stringify(fixture.candidates);
	for (const forbidden of ["credential", "secret", "personal data", "token", "password", "@", "https://"]) {
		assert.equal(serialized.toLowerCase().includes(forbidden), false, `fixture contains forbidden payload marker: ${forbidden}`);
	}
}

test("global seam fixtures name exactly the four approved global skill IDs", () => {
	assert.deepEqual(GLOBAL_SEAM_FIXTURES.map(({ skillId }) => skillId), GLOBAL_SEAM_IDS);
	assert.deepEqual([...new Set(GLOBAL_SEAM_FIXTURES.map(({ fixture }) => fixture.skillId))], GLOBAL_SEAM_IDS);
});

test("global seam fixtures and skill contracts preserve bounded advisory ranking", () => {
	for (const { skillId, fixture, skill } of GLOBAL_SEAM_FIXTURES) {
		const candidateIds = fixture.candidates.map(({ candidateId }) => candidateId);
		assert.equal(fixture.skillId, skillId);
		assert.ok(fixture.candidates.length >= 2 && fixture.candidates.length <= 50, `${skillId}: bounded candidates`);
		assert.equal(new Set(candidateIds).size, candidateIds.length, `${skillId}: unique candidate IDs`);
		for (const candidateId of candidateIds) {
			assert.match(candidateId, /^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$/, `${skillId}: opaque candidate ID`);
		}
		assert.equal(fixture.originalSetRetained, true, `${skillId}: retains original set`);
		assert.deepEqual(fixture.successfulProposalCandidateIds, candidateIds, `${skillId}: one success proposal per candidate`);
		assert.equal(fixture.instrumentedTool, "jev_rank", `${skillId}: only measured tool`);
		assert.equal(fixture.sensitivePayloadExcluded, true, `${skillId}: sensitive payload excluded`);
		assertFixtureContainsOnlySafeSyntheticContent(fixture);
		assert.deepEqual(fixture.fallback.statuses, ["unavailable", "malformed"], `${skillId}: manual fallback states`);
		assert.equal(fixture.outcomes.length, candidateIds.length, `${skillId}: each candidate has outcome or pending`);
		for (const outcome of fixture.outcomes) {
			assert.ok(candidateIds.includes(outcome.candidateId), `${skillId}: outcome belongs to original set`);
			assert.ok(["accepted", "overridden", "not_used", "pending"].includes(outcome.disposition), `${skillId}: explicit disposition or pending`);
		}
		for (const requiredText of fixture.requiredSkillText) {
			assert.ok(skill.includes(requiredText), `${skillId}: missing required seam instruction: ${requiredText}`);
		}
		assert.match(skill, /Only `jev_rank` is the measured Jev interface; never use raw shell or MCP Jev\./);
		assert.match(skill, /Do not send credentials, secrets, personal data, or unauthorized sensitive payloads\./);
		assert.match(skill, /If Jev-on is absent or `jev_rank` returns no proposals, use the original manual path/);
		assert.ok(skill.includes(fixture.finalVerification), `${skillId}: final verification unchanged`);
	}
});

test("each global seam fixture receives one proposal per candidate without persisting candidate bodies", async () => {
	for (const { skillId, fixture } of GLOBAL_SEAM_FIXTURES) {
		const stdout = JSON.stringify({
			answers: Object.fromEntries(fixture.candidates.map((_, index) => [
				`candidate_${index}`,
				{ score: fixture.candidates.length - index },
			])),
		});
		const { api, manager, processAdapter } = setup({ plans: [{ code: 0, stdout }] });
		const result = details(await api.invokeTool("jev_rank", {
			skillId,
			criterion: fixture.criterion,
			candidates: fixture.candidates,
		}));
		assert.equal(result.status, "succeeded");
		assert.deepEqual(result.proposals.map(({ candidateId }) => candidateId), fixture.successfulProposalCandidateIds);
		assert.deepEqual(processAdapter.calls[0].args, ["run", "-"]);
		for (const { body } of fixture.candidates) {
			assert.equal(JSON.stringify(manager.getBranch()).includes(body), false, `${skillId}: candidate body persisted`);
		}
	}
});

test("receiving-code-review visibly dispositions every original review comment", () => {
	const fixture = GLOBAL_SEAM_FIXTURES.find(({ skillId }) => skillId === "receiving-code-review").fixture;
	assert.equal(fixture.outcomes.every(({ disposition }) => disposition !== "pending"), true);
});
