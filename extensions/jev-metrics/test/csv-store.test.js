import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import * as fsPromises from "node:fs/promises";
import { dirname } from "node:path";
import test from "node:test";

import {
	CSV_HEADER,
	appendCloseout,
	getStorePath,
	readHistory,
	renderCloseoutRow,
} from "../lib/csv-store.js";
import { createFakeClock, createFilesystemFixture } from "./helpers.js";

const EXPECTED_HEADER = "schema_version,closed_at,session_id,leaf_id,skill_ids,attempts,successes,proposals,accepted,overridden,not_used,pending,invalid_events,coverage";
const FIXED_TIME = "2026-09-29T12:00:00.000Z";

function metrics(overrides = {}) {
	return {
		sessionId: "session-fixture-1",
		leafId: "leaf-fixture-1",
		coverage: "instrumented-only",
		total: {
			attempts: 2,
			successes: 1,
			proposals: 3,
			accepted: 2,
			overridden: 1,
			notUsed: 0,
			pending: 0,
			invalidEvents: 2,
			coverage: "instrumented-only",
		},
		bySkill: [
			{ scope: "speckit-tasks", attempts: 1 },
			{ scope: "receiving-code-review", attempts: 1 },
		],
		...overrides,
	};
}

function storeOptions(filesystem, overrides = {}) {
	return {
		projectRoot: filesystem.root,
		stateHome: filesystem.path("xdg-state"),
		clock: createFakeClock({ start: FIXED_TIME }),
		...overrides,
	};
}

test("renders the exact 14-column contract with extension time and sorted skill IDs", () => {
	assert.equal(CSV_HEADER, EXPECTED_HEADER);
	const row = renderCloseoutRow(metrics(), { clock: createFakeClock({ start: FIXED_TIME }) });
	assert.equal(
		row,
		"1,2026-09-29T12:00:00.000Z,session-fixture-1,leaf-fixture-1,receiving-code-review|speckit-tasks,2,1,3,2,1,0,0,2,instrumented-only",
	);
	assert.equal(row.split(",").length, 14);
});

test("uses RFC 4180 quoting while keeping UTF-8 and LF output", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const quoted = metrics({ sessionId: "session,\"quoted\"", leafId: "leaf\nline" });
	const result = await appendCloseout(quoted, storeOptions(filesystem));
	assert.equal(result.status, "appended");
	const path = await getStorePath(storeOptions(filesystem));
	const bytes = await fsPromises.readFile(path);
	const text = bytes.toString("utf8");
	assert.equal(Buffer.from(text, "utf8").equals(bytes), true);
	assert.equal(text.includes("\r"), false);
	assert.ok(text.endsWith("\n"));
	assert.ok(text.includes('"session,""quoted"""'));
	assert.ok(text.includes('"leaf\nline"'));
	const history = await readHistory(storeOptions(filesystem));
	assert.equal(history.storeState, "available");
	assert.equal(history.rows[0].session_id, quoted.sessionId);
	assert.equal(history.rows[0].leaf_id, quoted.leafId);
});

test("stores under the SHA-256 canonical-project partition and creates private state directory", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem);
	const canonicalRoot = await fsPromises.realpath(filesystem.root);
	const fingerprint = createHash("sha256").update(canonicalRoot).digest("hex");
	const path = await getStorePath(options);
	assert.equal(path, filesystem.path("xdg-state", "pi", "jev-metrics", `${fingerprint}.csv`));

	const result = await appendCloseout(metrics(), options);
	assert.equal(result.status, "appended");
	const text = await fsPromises.readFile(path, "utf8");
	assert.equal(text, `${EXPECTED_HEADER}\n${renderCloseoutRow(metrics(), options)}\n`);
	if (process.platform !== "win32") {
		const directoryMode = (await fsPromises.stat(dirname(path))).mode & 0o777;
		assert.equal(directoryMode & 0o077, 0, "state directory must not grant group/other permissions");
	}
});

test("uses an empty leaf only when Pi reports no leaf and empty skills when there was no attempt", () => {
	const empty = metrics({
		leafId: null,
		total: {
			attempts: 0,
			successes: 0,
			proposals: 0,
			accepted: 0,
			overridden: 0,
			notUsed: 0,
			pending: 0,
			invalidEvents: 0,
			coverage: "instrumented-only",
		},
		bySkill: [],
	});
	const row = renderCloseoutRow(empty, { clock: createFakeClock({ start: FIXED_TIME }) });
	assert.equal(row, `1,${FIXED_TIME},session-fixture-1,,,0,0,0,0,0,0,0,0,instrumented-only`);
	assert.throws(() => renderCloseoutRow({ ...empty, leafId: "" }, { clock: createFakeClock({ start: FIXED_TIME }) }), /leafId/i);
});

test("reads validated rows with typed session aggregate counters", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem);
	await appendCloseout(metrics(), options);
	const history = await readHistory(options);
	assert.deepEqual(history, {
		storeState: "available",
		rows: [{
			schema_version: 1,
			closed_at: FIXED_TIME,
			session_id: "session-fixture-1",
			leaf_id: "leaf-fixture-1",
			skill_ids: "receiving-code-review|speckit-tasks",
			attempts: 2,
			successes: 1,
			proposals: 3,
			accepted: 2,
			overridden: 1,
			not_used: 0,
			pending: 0,
			invalid_events: 2,
			coverage: "instrumented-only",
		}],
	});
});

test("returns available with zero rows only for a validated header-only store", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem);
	const path = await getStorePath(options);
	await fsPromises.mkdir(dirname(path), { recursive: true });
	await fsPromises.writeFile(path, `${EXPECTED_HEADER}\n`, "utf8");
	assert.deepEqual(await readHistory(options), { storeState: "available", rows: [] });
});

test("returns explicit missing and unreadable history states without historical zeroes", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem);
	assert.deepEqual(await readHistory(options), { storeState: "missing" });

	const denied = new Error("private path denied");
	denied.code = "EACCES";
	const fileSystem = { ...fsPromises, readFile: async () => { throw denied; } };
	assert.deepEqual(await readHistory({ ...options, fileSystem }), { storeState: "unreadable" });
});

test("appends one row per session ID and repeated closeout is already_exported", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem);
	assert.deepEqual(await appendCloseout(metrics(), options), {
		status: "appended",
		sessionId: "session-fixture-1",
		storeState: "available",
	});
	const path = await getStorePath(options);
	const first = await fsPromises.readFile(path, "utf8");
	assert.deepEqual(await appendCloseout(metrics(), options), {
		status: "already_exported",
		sessionId: "session-fixture-1",
		storeState: "available",
	});
	assert.equal(await fsPromises.readFile(path, "utf8"), first);
	assert.equal(first.trimEnd().split("\n").length, 2);
});

test("concurrent closeout rechecks session uniqueness while holding the lock", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const options = storeOptions(filesystem, { lockRetryMs: 1, lockAttempts: 100 });
	const results = await Promise.all([
		appendCloseout(metrics(), options),
		appendCloseout(metrics(), options),
	]);
	assert.deepEqual(results.map(({ status }) => status).sort(), ["already_exported", "appended"]);
	const history = await readHistory(options);
	assert.equal(history.storeState, "available");
	assert.equal(history.rows.length, 1);
});

test("flushes appended data before releasing the project lock", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const lifecycle = [];
	const fileSystem = {
		...fsPromises,
		async open(path, flags, mode) {
			const handle = await fsPromises.open(path, flags, mode);
			if (flags !== "a") return handle;
			return {
				writeFile: (...args) => handle.writeFile(...args),
				sync: async () => { lifecycle.push("sync"); await handle.sync(); },
				close: () => handle.close(),
			};
		},
		async rm(path, options) {
			if (path.endsWith(".lock")) lifecycle.push("unlock");
			return fsPromises.rm(path, options);
		},
	};
	const result = await appendCloseout(metrics(), storeOptions(filesystem, { fileSystem }));
	assert.equal(result.status, "appended");
	assert.deepEqual(lifecycle, ["sync", "unlock"]);
});

test("reports invalid stores and leaves corrupt headers or rows untouched", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	for (const [name, corrupt] of [
		["header", "wrong,header\n"],
		["row", `${EXPECTED_HEADER}\n1,not-a-time,session-x,,speckit-tasks,0,2,0,0,0,0,0,0,instrumented-only\n`],
	]) {
		const options = storeOptions(filesystem, { stateHome: filesystem.path(`state-${name}`) });
		const path = await getStorePath(options);
		await fsPromises.mkdir(dirname(path), { recursive: true });
		await fsPromises.writeFile(path, corrupt, "utf8");
		assert.deepEqual(await readHistory(options), { storeState: "invalid" });
		assert.deepEqual(await appendCloseout(metrics(), options), {
			status: "store_error",
			sessionId: "session-fixture-1",
			storeState: "invalid",
		});
		assert.equal(await fsPromises.readFile(path, "utf8"), corrupt);
	}
});

test("CSV body excludes project paths, fingerprints, and forbidden raw-data sentinels", async (t) => {
	const filesystem = await createFilesystemFixture();
	t.after(() => filesystem.cleanup());
	const sentinels = [
		"CANDIDATE_SENTINEL", "CRITERION_SENTINEL", "PROMPT_SENTINEL", "LOG_SENTINEL",
		"RAW_JEV_SENTINEL", "STDERR_SENTINEL", "CREDENTIAL_SENTINEL", "PERSONAL_SENTINEL",
		"https://provider.invalid",
	];
	const withForbiddenExtras = metrics({
		candidateBodies: sentinels,
		projectPath: filesystem.root,
	});
	const options = storeOptions(filesystem);
	await appendCloseout(withForbiddenExtras, options);
	const path = await getStorePath(options);
	const text = await fsPromises.readFile(path, "utf8");
	const canonicalRoot = await fsPromises.realpath(filesystem.root);
	const fingerprint = createHash("sha256").update(canonicalRoot).digest("hex");
	assert.equal(text.includes(filesystem.root), false);
	assert.equal(text.includes(canonicalRoot), false);
	assert.equal(text.includes(fingerprint), false);
	for (const sentinel of sentinels) assert.equal(text.includes(sentinel), false);
});
