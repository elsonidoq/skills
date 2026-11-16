// Skill-preservation review: nine skills, two fresh agents per skill, sequentially.
// This file is a pi-subagents workflow body, not a standalone Node.js program.
//
// Python reading guide:
//   const = a local variable; for (... of ...) = for ... in ...; await = wait.
//   runs.run(key, settings) starts a child and returns its completed result.
//   args contains the inputs supplied by the caller. pi-subagents supplies runs.
//
// Launch this WORKFLOW in the background (async: true). Child calls below omit
// their async flag deliberately: await then receives a finished report, not just
// a launch receipt. The workflow runs in the background while it waits.
// No agents are resumed, no automatic retries, no files edited by the agents.
//
// Required inputs: projectRoot and candidateRevision (a frozen full Git SHA).
// Optional input: originalRevision; default is the pre-simplification revision.
// Example launch through the subagent tool (do not run this as a shell command):
// { workflow: "./scripts/review-skill-preservation.workflow.js", async: true,
//   args: { projectRoot: "/absolute/checkout", candidateRevision: "FULL_SHA" } }

const originalRevision = args.originalRevision || "aad2c8a32421580ee70e28197c2b12b3e93314c0";
const candidateRevision = args.candidateRevision;
const projectRoot = args.projectRoot;
const model = "openai-codex/gpt-6-astra:medium";

// Exact revisions prevent moving HEAD from changing what different agents read.
if (!projectRoot || !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(originalRevision) ||
    !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(candidateRevision)) {
  throw new Error("Supply projectRoot and full original/candidate Git commit SHAs.");
}

const skills = [
  "task-generation",
  "planning-brainstorming",
  "tiny-spec",
  "delegating-architectural-planning",
  "planner",
  "writing-skills",
  "finish-session",
  "track-open-issue",
  "handoff-prompt",
];

// A normally exited agent can still report that it could not do its job.
// This small result contract distinguishes completed analysis from a blocker.
const reportFormat = {
  type: "object",
  properties: {
    status: { type: "string", enum: ["complete", "blocked"] },
    report: { type: "string" },
  },
  required: ["status", "report"],
  additionalProperties: false,
};

const readOnlyRules = `
Read-only analysis. Read Git objects with git show REVISION:path; do not treat
working-tree files as the selected revision. Verify the commit exists first.
Use only the assigned skill and necessary referenced owners, instructions and
accepted decisions at that revision. Follow links only as needed. Never edit,
commit, push, install, authenticate, delegate, launch a workflow, or run live tests.
If evidence is unavailable or materially ambiguous, report it explicitly. Do not
invent behavior, approvals or evidence. Return status=blocked if you cannot
complete the assigned analysis; findings themselves do not mean blocked.
`;

function completedReport(result, stage) {
  const data = result.structuredOutput;
  if (!result.ok || !data || data.status !== "complete" || !data.report.trim()) {
    throw new Error(`${stage} stopped; inspect run ${result.runId} and ${result.outputReference}. No retry was launched.`);
  }
  return data.report;
}

const results = [];
for (const skill of skills) {
  const path = `skills/${skill}/SKILL.md`;

  // 1. Extract a rubric WITHOUT seeing the replacement or its author's rationale.
  const extraction = await runs.run(`${skill}-extract`, {
    agent: "coherence-reviewer",
    model,
    context: "fresh",
    cwd: projectRoot,
    output: `reports/${skill}-original-rubric.json`,
    outputMode: "file-only",
    outputSchema: reportFormat,
    task: `Extract intended behavior from ${originalRevision}:${path}.
${readOnlyRules}
Do not read the replacement, current working-tree skill, change diff, author
reports or later revisions. Establish the original contract before judging any
rewrite. Return a compact numbered rubric: each item states one behavioral
obligation, its condition/applicability, and a supporting revision:path:line citation.
Cover job/trigger, inputs, decisions, outputs/consumer, authority/approval boundaries,
conditional/standalone/recovery routes and relevant guarantees. Distinguish behavior
owned here from behavior obtained from an existing canonical owner. Capture actual
behavior, not headings, repeated wording or incidental examples. Expose conflicts
and uncertainty; do not silently decide which original obligation to discard.
`,
  });
  const rubric = completedReport(extraction, `${skill}: original extraction`);

  // 2. A DIFFERENT fresh agent checks the replacement against that frozen rubric.
  const review = await runs.run(`${skill}-review`, {
    agent: "coherence-reviewer",
    model,
    context: "fresh",
    cwd: projectRoot,
    output: `reports/${skill}-preservation-review.json`,
    outputMode: "file-only",
    outputSchema: reportFormat,
    task: `Review ${candidateRevision}:${path} against the original rubric below.
${readOnlyRules}
Read the replacement and necessary owners at the candidate revision. For EACH
rubric ID report: preserved directly, preserved through an existing owner, changed
or missing, or uncertain. Cite candidate evidence. For an existing-owner result,
verify the owner actually supplies the behavior and the skill invokes it at the
right boundary and consumes its result. A bare link is insufficient.
Consult cited original evidence at ${originalRevision} to resolve ambiguity or
suspected extraction errors; distinguish rubric defects from rewrite defects.
Also check for new unintended obligations, broken callers/anchors and complexity
merely relocated into references. Preserve required behavior, not old structure.
Return coverage, supported findings with impact and smallest correction, and gaps.
Do not infer equivalence or live model obedience from static reading.

FROZEN ORIGINAL RUBRIC:
${rubric}
`,
  });
  completedReport(review, `${skill}: replacement review`);

  // Return report locations, not eighteen full agent reports in the conversation.
  results.push({
    skill,
    originalRevision,
    candidateRevision,
    extractionRun: extraction.runId,
    rubric: extraction.outputReference,
    reviewRun: review.runId,
    review: review.outputReference,
  });
}

// Completing the workflow means all analyses returned, NOT that all skills passed.
// The saved per-skill reports contain findings; acceptance is a separate decision.
return results;
