import {
	APPROVED_SKILL_IDS,
	CANDIDATE_ID_PATTERN,
	createInvocationStart,
	createInvocationTerminal,
} from "./events.js";

export const SCORE_LEVELS = Object.freeze([
	"No support for the criterion",
	"Weak support for the criterion",
	"Moderate support for the criterion",
	"Strong support for the criterion",
	"Very strong support for the criterion",
]);

export const EXIT_FAILURES = Object.freeze({
	1: Object.freeze({ status: "failed", failureClass: "provider" }),
	2: Object.freeze({ status: "failed", failureClass: "input" }),
	3: Object.freeze({ status: "unavailable", failureClass: "auth" }),
	4: Object.freeze({ status: "failed", failureClass: "retryable" }),
});

export class JevInputError extends TypeError {
	constructor(message) {
		super(message);
		this.name = "JevInputError";
		this.reason = "input";
	}
}

export class JevResponseError extends TypeError {
	constructor(message) {
		super(message);
		this.name = "JevResponseError";
		this.reason = "response_schema";
	}
}

function inputError(message) {
	throw new JevInputError(message);
}

function responseError(message) {
	throw new JevResponseError(message);
}

function isObject(value) {
	return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateRankingInput({ sessionId, skillId, criterion, candidates } = {}) {
	if (typeof sessionId !== "string" || sessionId.length < 1 || sessionId.length > 256) {
		inputError("sessionId must be a non-empty string of at most 256 characters");
	}
	if (!APPROVED_SKILL_IDS.includes(skillId)) inputError("skillId is not approved");
	if (typeof criterion !== "string" || criterion.trim().length === 0) {
		inputError("criterion must be a non-empty string");
	}
	if (!Array.isArray(candidates) || candidates.length < 2 || candidates.length > 50) {
		inputError("candidates must contain 2 through 50 entries");
	}
	const candidateIds = new Set();
	for (const candidate of candidates) {
		if (!isObject(candidate)) inputError("each candidate must be an object");
		if (typeof candidate.candidateId !== "string" || !CANDIDATE_ID_PATTERN.test(candidate.candidateId)) {
			inputError("candidateId is invalid");
		}
		if (candidateIds.has(candidate.candidateId)) inputError("candidateIds must be unique");
		if (typeof candidate.body !== "string") inputError("candidate body must be a string");
		candidateIds.add(candidate.candidateId);
	}
}

/** Build the complete Jev 0.6.3 request. Candidate content exists only in this transient object. */
export function buildJevRequest(input) {
	validateRankingInput(input);
	const { criterion, candidates } = input;
	return {
		state: {
			criterion,
			candidates: candidates.map(({ candidateId, body }) => ({ candidateId, body })),
		},
		questions: Object.fromEntries(candidates.map(({ candidateId }, index) => [
			`candidate_${index}`,
			{
				type: "score",
				instructions: `${criterion} Candidate: ${candidateId}.`,
				criteria: SCORE_LEVELS,
			},
		])),
	};
}

/** Validate Jev answers and return only candidate IDs plus normalized numeric result fields. */
export function normalizeJevResponse(response, candidates) {
	if (!isObject(response) || !isObject(response.answers)) responseError("response.answers must be an object");
	if (!Array.isArray(candidates) || candidates.length < 2 || candidates.length > 50) {
		responseError("candidate context is invalid");
	}
	const expectedKeys = candidates.map((_, index) => `candidate_${index}`);
	const actualKeys = Object.keys(response.answers);
	if (actualKeys.length !== expectedKeys.length || expectedKeys.some((key) => !Object.hasOwn(response.answers, key))) {
		responseError("response must contain exactly one answer per candidate");
	}

	const scored = candidates.map(({ candidateId }, index) => {
		const answer = response.answers[`candidate_${index}`];
		if (!isObject(answer) || !Number.isFinite(answer.score)) responseError("answer score must be finite");
		if (Object.hasOwn(answer, "confidence") &&
			(!Number.isFinite(answer.confidence) || answer.confidence < 0 || answer.confidence > 1)) {
			responseError("answer confidence must be finite and between 0 and 1");
		}
		const normalized = { candidateId, score: answer.score, originalIndex: index };
		if (Object.hasOwn(answer, "confidence")) normalized.confidence = answer.confidence;
		return normalized;
	});

	scored.sort((left, right) => right.score - left.score || left.originalIndex - right.originalIndex);
	return scored.map(({ candidateId, score, confidence }, index) => {
		const proposal = { candidateId, rank: index + 1, score };
		if (confidence !== undefined) proposal.confidence = confidence;
		return proposal;
	});
}

function processFailure(error) {
	if (error?.code === "ENOENT") return { status: "unavailable", failureClass: "cli_missing" };
	if (error?.name === "AbortError" || error?.code === "ABORT_ERR") {
		return { status: "failed", failureClass: "cancelled" };
	}
	return { status: "failed", failureClass: "provider" };
}

async function emit(onEvent, event) {
	if (onEvent !== undefined) await onEvent(event);
}

/**
 * Run one tracked ranking invocation through an injected process adapter.
 * Only privacy-safe start/terminal events are returned or emitted.
 */
export async function runJevRanking(
	input,
	{
		processAdapter,
		clock,
		uuid,
		executable = "jev",
		signal,
		onEvent,
		eventIds,
		invocationIds,
	} = {},
) {
	const request = buildJevRequest(input);
	if (!processAdapter || typeof processAdapter.run !== "function") {
		throw new TypeError("processAdapter.run is required");
	}
	if (typeof executable !== "string" || executable.length === 0) {
		throw new TypeError("executable must be a non-empty string");
	}

	const start = createInvocationStart({
		sessionId: input.sessionId,
		skillId: input.skillId,
		candidateIds: input.candidates.map(({ candidateId }) => candidateId),
	}, { clock, uuid, eventIds, invocationIds });
	await emit(onEvent, start);

	let terminalInput;
	try {
		const processResult = await processAdapter.run(executable, ["run", "-"], {
			input: JSON.stringify(request),
			signal,
			shell: false,
		});
		if (processResult.code !== 0) {
			terminalInput = EXIT_FAILURES[processResult.code] ?? { status: "failed", failureClass: "provider" };
		} else {
			try {
				const response = JSON.parse(processResult.stdout);
				terminalInput = {
					status: "succeeded",
					proposals: normalizeJevResponse(response, input.candidates),
				};
			} catch {
				terminalInput = { status: "malformed", failureClass: "response_schema" };
			}
		}
	} catch (error) {
		terminalInput = processFailure(error);
	}

	const terminal = createInvocationTerminal({
		start,
		status: terminalInput.status,
		failureClass: terminalInput.failureClass,
		proposals: terminalInput.proposals ?? [],
	}, { clock, uuid, eventIds });
	await emit(onEvent, terminal);
	return Object.freeze({ start, terminal });
}
