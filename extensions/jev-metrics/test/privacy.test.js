import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { CSV_COLUMNS, getStorePath, parseHistoryCsv } from "../lib/csv-store.js";
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

const EVENT_FIELDS = {
	invocation_started: ["schemaVersion", "eventType", "eventId", "invocationId", "sessionId", "skillId", "startedAt", "candidateIds"],
	invocation_terminal: ["schemaVersion", "eventType", "eventId", "invocationId", "sessionId", "finishedAt", "status", "failureClass", "proposals"],
	proposal_disposition: ["schemaVersion", "eventType", "eventId", "proposalId", "sessionId", "skillId", "disposition", "recordedAt"],
	invalid_event: ["schemaVersion", "eventType", "eventId", "sessionId", "operation", "reason", "recordedAt"],
};
const PROPOSAL_FIELDS = ["proposalId", "candidateId", "rank", "score", "confidence"];
const SENTINELS = {
	candidate: "CANDIDATE_BODY_SENTINEL",
	criterion: "CRITERION_SENTINEL",
	log: "LOG_SENTINEL",
	credential: "CREDENTIAL_SECRET_SENTINEL",
	personal: "PERSONAL_DATA_SENTINEL",
	stderr: "STDERR_SENTINEL",
	endpoint: "https://private-provider.invalid/v1",
	rawResponse: "RAW_RESPONSE_SENTINEL",
};

function assertExactFields(value, allowed) {
	for (const field of Object.keys(value)) {
		assert.ok(allowed.includes(field), `unexpected persisted field: ${field}`);
	}
}

function assertNoSentinels(value, extra = []) {
	const serialized = typeof value === "string" ? value : JSON.stringify(value);
	for (const sentinel of [...Object.values(SENTINELS), ...extra]) {
		assert.equal(serialized.includes(sentinel), false, `leaked sentinel: ${sentinel}`);
	}
}

test("session entries, diagnostics, metrics output, and CSV retain only approved telemetry", async (t) => {
	const filesystem = await createFilesystemFixture({ prefix: "PROJECT_PATH_SENTINEL-" });
	t.after(() => filesystem.cleanup());
	const manager = new FakeSessionManager({ cwd: filesystem.root });
	const context = createFakeExtensionContext({ sessionManager: manager, cwd: filesystem.root });
	const api = new FakeExtensionAPI({ context });
	const rawStdout = `{\"${SENTINELS.rawResponse}\":\"${SENTINELS.endpoint}\"}`;
	const processAdapter = createFakeProcessAdapter([{
		code: 0,
		stdout: rawStdout,
		stderr: `${SENTINELS.stderr} ${SENTINELS.credential}`,
	}]);
	createJevMetricsExtension({
		processAdapter,
		clock: createFakeClock(),
		uuid: createUuidSource(),
		stateHome: filesystem.path("state"),
	})(api);

	const rankResult = await api.invokeTool("jev_rank", {
		skillId: "receiving-code-review",
		criterion: `${SENTINELS.criterion} ${SENTINELS.log}`,
		candidates: [
			{ candidateId: "opaque-1", body: `${SENTINELS.candidate} ${SENTINELS.personal}` },
			{ candidateId: "opaque-2", body: `${SENTINELS.credential} ${SENTINELS.endpoint}` },
		],
	});
	assert.equal(rankResult.details.status, "malformed");
	assertNoSentinels(rankResult);

	const diagnostic = await api.invokeTool("jev_disposition", {
		proposalId: `${SENTINELS.rawResponse}:proposal:unknown`,
		disposition: "accepted",
	});
	assert.deepEqual(diagnostic.details, { recorded: false, reason: "unknown_proposal" });
	assertNoSentinels(diagnostic);

	const entries = manager.getBranch();
	assert.deepEqual(entries.map(({ data }) => data.eventType), [
		"invocation_started",
		"invocation_terminal",
		"invalid_event",
	]);
	for (const { data: event } of entries) {
		assertExactFields(event, EVENT_FIELDS[event.eventType]);
		if (event.eventType === "invocation_terminal") {
			for (const proposal of event.proposals) assertExactFields(proposal, PROPOSAL_FIELDS);
		}
	}
	assertNoSentinels(entries, [filesystem.root]);

	const metrics = await api.invokeTool("jev_metrics", { action: "current" });
	assertExactFields(metrics.details, ["sessionId", "leafId", "coverage", "coverageNotice", "eventState", "total", "bySkill"]);
	assertExactFields(metrics.details.total, ["attempts", "successes", "proposals", "accepted", "overridden", "notUsed", "pending", "invalidEvents"]);
	for (const skill of metrics.details.bySkill) {
		assertExactFields(skill, ["scope", "attempts", "successes", "proposals", "accepted", "overridden", "notUsed", "pending", "invalidEvents"]);
	}
	assertNoSentinels(metrics, [filesystem.root]);

	const commandText = await api.invokeCommand("jev-metrics", "");
	assertNoSentinels(commandText, [filesystem.root]);

	const closeout = await api.invokeTool("jev_metrics", { action: "closeout" });
	assert.equal(closeout.details.status, "appended");
	assertNoSentinels(closeout, [filesystem.root]);
	const csvPath = await getStorePath({ projectRoot: filesystem.root, stateHome: filesystem.path("state") });
	const csv = await readFile(csvPath, "utf8");
	assertNoSentinels(csv, [filesystem.root]);
	const records = parseHistoryCsv(csv);
	assert.equal(records.length, 1);
	assertExactFields(records[0], CSV_COLUMNS);
});

test("allowlist rejects any field outside approved telemetry and CSV contracts", () => {
	assert.throws(() => assertExactFields({ eventType: "invalid_event", rawError: "forbidden" }, EVENT_FIELDS.invalid_event), /unexpected persisted field/);
	assert.throws(() => assertExactFields({ schema_version: 1, project_path: "forbidden" }, CSV_COLUMNS), /unexpected persisted field/);
});
