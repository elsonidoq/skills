// Narrow repairs after the original extraction/review workflow.
// Run this workflow in the background through pi-subagents, not with Node.js.
//
// For each affected skill, in order:
//   1. A fresh Astra/medium author assesses the existing findings, repairs justified
//      omissions, runs affected checks, and commits only that skill's changes.
//   2. Its ORIGINAL reviewer is resumed to check the delta and declined findings.
// Stop on a blocked author/reviewer. No automatic retry or re-extraction.
//
// Inputs: projectRoot, reviewDirectory (the original saved reports), startRevision
// (full current Git SHA). Reports are saved by pi-subagents, not by the agents.
// runs.run is supplied by pi-subagents; await receives a completed child result.
// Explicit child async flags are omitted to avoid receiving launch receipts.

const model = "openai-codex/gpt-6-astra:medium";
const originalRevision = "aad2c8a32421580ee70e28197c2b12b3e93314c0";
const reviewedRevision = "7b1ce123eecd79540d6a881cd38210ec76a44c5c";
const { projectRoot, reviewDirectory, startRevision } = args;
if (!projectRoot || !reviewDirectory || !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(startRevision)) {
  throw new Error("Supply projectRoot, the original reviewDirectory, and a full startRevision SHA.");
}

// These are the six skills with findings, not a second review of all nine skills.
const repairs = [
  {
    skill: "task-generation",
    reviewer: "49f6cd21-6fcf-4170-847e-3a5c6f7fa3fa",
    focus: "F1: ownership when owned_paths is absent. Prefer a clear invocation of the existing execution owner over copying runtime implementation detail.",
  },
  {
    skill: "planning-brainstorming",
    reviewer: "28534596-f52e-476d-9630-10f547d25206",
    focus: "F1: retention of source bounds, decisions, deferrals and handoff. F2: execution-only rules must not become planning prerequisites. Assess capability-check timing against the approved operation-boundary approach; do not blindly restore blanket preflight.",
  },
  {
    skill: "delegating-architectural-planning",
    reviewer: "c17cf260-3d68-422e-8116-8ad0374db607",
    focus: "F1: explicitly transfer the already-discovered input package to the fresh producer, including standalone entry. No new artifact or repeated discovery.",
  },
  {
    skill: "planner",
    reviewer: "91685daf-51b3-4261-9cbb-ba477aaae020",
    focus: "F1: artifact-destination discovery follows depth selection. Restore only the bounded timing rule, not another gate.",
  },
  {
    skill: "writing-skills",
    reviewer: "c0bd3ee6-e67d-475a-974d-cb8f555fe301",
    focus: "F1: make purpose/core decisions discoverable without reinstating old structure. F2: permit bounded revisions; fresh reconstruction is appropriate for bloated procedures, not every material edit. Preserve proportionate validation rather than the original contradictory paired-run mandate.",
  },
  {
    skill: "finish-session",
    reviewer: "5a90a0d0-fdba-4e60-bb08-4909ecee778c",
    focus: "F1: distinguish plausible deployment implications requiring bounded triage from concrete implications permitting deployment-owner inspection. Keep unknowns visible without creating an audit.",
  },
];

const authorFormat = {
  type: "object",
  properties: {
    status: { type: "string", enum: ["complete", "blocked"] },
    baselineRevision: { type: "string" },
    resultRevision: { type: "string" },
    report: { type: "string" },
  },
  required: ["status", "baselineRevision", "resultRevision", "report"],
  additionalProperties: false,
};

function completed(result, stage) {
  const data = result.structuredOutput;
  if (!result.ok || !data || data.status !== "complete" || !data.report.trim()) {
    throw new Error(`${stage} stopped. Inspect run ${result.runId}, report ${result.outputReference}; no retry was launched.`);
  }
  return data;
}

let baseline = startRevision;
const results = [];
for (const repair of repairs) {
  const skillPath = `skills/${repair.skill}/SKILL.md`;
  const rubricPath = `${reviewDirectory}/${repair.skill}-original-rubric.json`;
  const findingsPath = `${reviewDirectory}/${repair.skill}-preservation-review.json`;

  const author = await runs.run(`${repair.skill}-repair`, {
    agent: "worker",
    model,
    context: "fresh",
    cwd: projectRoot,
    output: `repairs/${repair.skill}-author.json`,
    outputMode: "file-only",
    outputSchema: authorFormat,
    task: `Assess and repair ONLY the existing findings for ${skillPath}.
Current expected HEAD: ${baseline}. Original: ${originalRevision}.
Previously reviewed candidate: ${reviewedRevision}.
Read ${rubricPath} and ${findingsPath}, the actual original/candidate evidence,
and the current skill and relevant existing owners before deciding.
Focus: ${repair.focus}

The owner authorizes narrow behavior-preserving repairs, verification and a focused
local commit. This is not permission to reauthor the whole skill, change unrelated
behavior, or mechanically restore every deleted sentence. Keep the clarity gains.
For each finding: confirm its basis, make the smallest justified correction, or
explain why it is already covered, intentional or unsupported. An unresolved material
scope/authority conflict is blocked, not consent to change policy.

Read AGENTS.md, the project memory index and matching entries, receiving-code-review,
writing-skills, decision index and accepted ADR-0003/0004, and task-commit contract.
Use current scoped authority; ordinary diagnosed test repairs need no new approval.
Preserve unrelated tracked/untracked work and all other skill changes.

Owned skill: ${skillPath}. Coupled test edits allowed only for this repair in
scripts/check-planner-workflow.py, scripts/test-planner-workflow.py and the skill's
existing scripts/test_contract.py. If finish-session affects tracker expectations,
its existing contract suite may be adjusted narrowly too. No other skill/reference,
runtime, assignment, policy, workflow, history or configuration edits. No new
reference library, report ledger, STATE or progress file. Do not delegate, launch
workflows, install, authenticate, access secrets, push, merge, mutate trackers,
activate globally or touch Railway/Cerca. Unlisted substantive support changes
need scope resolution; do not silently expand.

Run python3 scripts/check-planner-workflow.py and
python3 scripts/test-planner-workflow.py; run the relevant existing skill-local
contract tests and task-order/tracker tests when their actual seam is affected.
Inspect changed links/callers and diff whitespace. Preserve meaningful test
sensitivity, not exact old prose. Explain unavailable or failed verification.
Existing isolated offline checks are authorized; live trials are not.

Verify HEAD equals the expected baseline before edits. After actual passes, inspect
the diff and create one focused explicit-path commit with normal hooks/signing.
No broad staging, reset, cleanup, identity changes, empty commits or history rewrite.
If every finding is validly declined, make no empty commit and return the same SHA.
Return status complete only when every finding has a supported disposition, checks
are satisfied and task-owned state is clean. Include full baseline/result SHAs,
paths, dispositions, checks/results/limits and residual state. Failure means blocked;
retain work and report its exact cause. Do not proceed to another skill yourself.
`,
  });
  const change = completed(author, `${repair.skill}: repair`);
  if (change.baselineRevision !== baseline ||
      !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(change.resultRevision)) {
    throw new Error(`Inspect ${repair.skill} author revision report before continuing.`);
  }

  // Resume the exact existing reviewer: no new rubric or full-range review.
  const recheck = await runs.run(`${repair.skill}-recheck`, {
    resume: repair.reviewer,
    output: `repairs/${repair.skill}-targeted-recheck.json`,
    outputMode: "file-only",
    task: `Targeted repair recheck requested by the owner, not a new full review.
Retain your original rubric coverage and findings. Read only the actual delta
${change.baselineRevision}..${change.resultRevision}, necessary affected interactions
and the author's finding dispositions below. Check all original findings for this
skill, including declined ones. Do not repeat unchanged extraction or full review.
Verify actual Git commit parent/path facts and task-owned residual state; author
claims alone are not evidence. Report any new defect caused by the repair.

Remain read-only: no edits, commits, providers/tests, external actions or delegation.
Do not demand new machinery or restore original contradictions. Current owner
scope preserves clarity and behavior, not old wording/structure. The author has
no authority for runtime/global/policy changes or live trial.

Keep the existing status/report output format. FOR THIS RECHECK status complete
means the findings are resolved or validly declined with evidence, with no material
repair defect or coverage gap. Otherwise return status blocked and explain the
remaining issue. This overrides the earlier analysis-only status semantics for
this recheck; unresolved findings must stop the repair sequence. No automatic retry.
Return each disposition and concise evidence/limits. Author report:
${change.report}
`,
  });
  completed(recheck, `${repair.skill}: targeted recheck`);

  results.push({
    skill: repair.skill,
    baselineRevision: change.baselineRevision,
    resultRevision: change.resultRevision,
    authorRun: author.runId,
    authorReport: author.outputReference,
    reviewerRun: recheck.runId,
    reviewerReport: recheck.outputReference,
  });
  baseline = change.resultRevision;
}

// This is technical repair completion, not owner acceptance or live behavior proof.
return results;
