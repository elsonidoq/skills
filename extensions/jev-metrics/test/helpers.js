import { access, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";

const DEFAULT_TIME = "2026-01-01T00:00:00.000Z";

/** A deterministic clock; advancing is always explicit. */
export function createFakeClock({ start = DEFAULT_TIME } = {}) {
	let milliseconds = new Date(start).getTime();
	if (!Number.isFinite(milliseconds)) {
		throw new TypeError("start must be a valid date");
	}

	return {
		now: () => new Date(milliseconds),
		iso: () => new Date(milliseconds).toISOString(),
		advance: (duration) => {
			if (!Number.isFinite(duration)) throw new TypeError("duration must be finite");
			milliseconds += duration;
			return new Date(milliseconds);
		},
		set: (value) => {
			const next = new Date(value).getTime();
			if (!Number.isFinite(next)) throw new TypeError("value must be a valid date");
			milliseconds = next;
			return new Date(milliseconds);
		},
	};
}

/** A deterministic UUID v4-shaped source suitable for schema-valid fixtures. */
export function createUuidSource({ start = 1 } = {}) {
	let counter = start;
	if (!Number.isSafeInteger(counter) || counter < 0) {
		throw new TypeError("start must be a non-negative safe integer");
	}

	const next = () => {
		const value = counter.toString(16).padStart(12, "0");
		if (value.length > 12) throw new RangeError("fake UUID source exhausted");
		counter += 1;
		return `00000000-0000-4000-8000-${value}`;
	};

	return {
		next,
		uuid: next,
		reset: (value = start) => {
			if (!Number.isSafeInteger(value) || value < 0) {
				throw new TypeError("reset value must be a non-negative safe integer");
			}
			counter = value;
		},
	};
}

function abortError() {
	const error = new Error("The fake process was cancelled");
	error.name = "AbortError";
	error.code = "ABORT_ERR";
	return error;
}

function normalizeProcessResult(result = {}) {
	return {
		code: result.code ?? result.exitCode ?? 0,
		stdout: result.stdout ?? "",
		stderr: result.stderr ?? "",
		signal: result.signal ?? null,
	};
}

/**
 * An injectable process boundary. Plans are consumed in order and are never
 * executed as commands. A plan may be a result object, an Error, or a function
 * receiving the recorded call.
 */
export function createFakeProcessAdapter(plans = []) {
	const queue = [...plans];
	const calls = [];

	return {
		calls,
		enqueue: (plan) => queue.push(plan),
		remaining: () => queue.length,
		async run(command, args = [], options = {}) {
			const call = {
				command,
				args: [...args],
				input: options.input ?? options.stdin ?? "",
			};
			calls.push(call);

			if (options.signal?.aborted) throw abortError();
			if (queue.length === 0) {
				throw new Error("No fake process plan was queued");
			}

			let plan = queue.shift();
			if (typeof plan === "function") plan = await plan(call);
			if (plan instanceof Error) throw plan;
			if (plan?.cancelled) throw abortError();
			return normalizeProcessResult(plan);
		},
	};
}

/** Minimal active-branch session manager matching the Pi extension surface. */
export class FakeSessionManager {
	constructor({ sessionId = "session-fixture-1", leafId = "leaf-fixture-1", branch = [], cwd = process.cwd() } = {}) {
		this.sessionId = sessionId;
		this.leafId = leafId;
		this.cwd = cwd;
		this.branch = [...branch];
		this.entryCounter = this.branch.length;
	}

	getSessionId() {
		return this.sessionId;
	}

	getLeafId() {
		return this.leafId;
	}

	getCwd() {
		return this.cwd;
	}

	getBranch() {
		return [...this.branch];
	}

	setBranch(branch, { leafId = this.leafId } = {}) {
		this.branch = [...branch];
		this.leafId = leafId;
		this.entryCounter = this.branch.length;
	}

	setSession({ sessionId = this.sessionId, leafId = this.leafId } = {}) {
		this.sessionId = sessionId;
		this.leafId = leafId;
	}

	appendCustomEntry(customType, data) {
		this.entryCounter += 1;
		const entry = {
			id: `fake-entry-${this.entryCounter}`,
			parentId: this.leafId,
			timestamp: DEFAULT_TIME,
			type: "custom",
			customType,
			data,
		};
		this.branch.push(entry);
		this.leafId = entry.id;
		return entry.id;
	}
}

/** Construct only the ExtensionContext fields used by the metric extension tests. */
export function createFakeExtensionContext({ sessionManager, cwd, ...context } = {}) {
	const manager = sessionManager ?? new FakeSessionManager({ cwd });
	const notifications = [];
	return {
		sessionManager: manager,
		cwd: cwd ?? manager.getCwd(),
		hasUI: false,
		ui: {
			notifications,
			notify: (message, level = "info") => notifications.push({ message, level }),
		},
		...context,
	};
}

/**
 * Captures Pi registrations and routes appendEntry calls into the fake active
 * branch. It intentionally has no provider, shell, or network capability.
 */
export class FakeExtensionAPI {
	constructor({ context = createFakeExtensionContext() } = {}) {
		this.context = context;
		this.tools = new Map();
		this.commands = new Map();
		this.handlers = new Map();
	}

	registerTool(tool) {
		if (!tool?.name) throw new TypeError("tool registration requires a name");
		if (this.tools.has(tool.name)) throw new Error(`duplicate tool: ${tool.name}`);
		this.tools.set(tool.name, tool);
	}

	registerCommand(name, options) {
		const command = typeof name === "string" ? { name, ...options } : name;
		if (!command?.name) throw new TypeError("command registration requires a name");
		if (this.commands.has(command.name)) throw new Error(`duplicate command: ${command.name}`);
		this.commands.set(command.name, command);
	}

	on(eventName, handler) {
		const handlers = this.handlers.get(eventName) ?? [];
		handlers.push(handler);
		this.handlers.set(eventName, handlers);
	}

	appendEntry(customType, data) {
		return this.context.sessionManager.appendCustomEntry(customType, data);
	}

	async emit(eventName, event = {}) {
		for (const handler of this.handlers.get(eventName) ?? []) {
			await handler(event, this.context);
		}
	}

	async invokeTool(name, params, { toolCallId = "tool-call-fixture-1", signal, onUpdate = () => {} } = {}) {
		const tool = this.tools.get(name);
		if (!tool) throw new Error(`unknown tool: ${name}`);
		return tool.execute(toolCallId, params, signal, onUpdate, this.context);
	}

	async invokeCommand(name, args = "") {
		const command = this.commands.get(name);
		if (!command) throw new Error(`unknown command: ${name}`);
		return command.handler(args, this.context);
	}
}

function fixturePath(root, file) {
	const resolved = resolve(root, file);
	if (relative(root, resolved).startsWith("..")) {
		throw new RangeError("fixture path must stay inside its temporary root");
	}
	return resolved;
}

/** A temporary, cleanup-owning filesystem fixture for CSV and store tests. */
export async function createFilesystemFixture({ prefix = "jev-metrics-" } = {}) {
	const root = await mkdtemp(join(tmpdir(), prefix));
	return {
		root,
		path: (...parts) => fixturePath(root, join(...parts)),
		async write(file, contents) {
			const target = fixturePath(root, file);
			await mkdir(dirname(target), { recursive: true });
			await writeFile(target, contents);
		},
		read: (file) => readFile(fixturePath(root, file), "utf8"),
		exists: async (file) => {
			try {
				await access(fixturePath(root, file));
				return true;
			} catch {
				return false;
			}
		},
		remove: (file) => rm(fixturePath(root, file), { force: true, recursive: true }),
		cleanup: () => rm(root, { force: true, recursive: true }),
		name: basename(root),
	};
}
