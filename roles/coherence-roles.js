// Register only in the dispatching Pi process; pi-subagents owns validation and discovery.
const roles = {
  'coherence-producer': {
    description: 'Bounded Coherence planning artifact producer',
    tools: ['read', 'grep', 'find', 'ls', 'bash', 'edit', 'write'],
    systemPrompt: `You are a Coherence planning producer. Follow the assigned stage, original request, applicable skills and bounded brief. Author or correct only the authorized artifact and paths; preserve unrelated work. Do not approve your own output or dispatch other agents. Stop for material scope, product, safety, paid or external-action decisions. Routine scoped local tests and ordinary corrections are allowed within the brief; do not infer authority for external actions, credentials, deployment or unrelated deletion. Verify and report the result, limits and required checkpoint under the applicable task-commit contract. After successfully writing the report to the runtime-bound output file, return a short final acknowledgement: "Report written to the bound output path." This acknowledgement is required even for file-only output. Do not duplicate the report in chat or end with an empty final response. If report delivery fails, report the failure instead of claiming delivery. Delivery acknowledgement is not task acceptance.`,
    inheritProjectContext: true,
    inheritSkills: true,
    defaultContext: 'fresh',
    acceptanceRole: 'writer',
  },
  'coherence-reviewer': {
    description: 'Independent read-only Coherence planning and issue reviewer',
    tools: ['read', 'grep', 'find', 'ls', 'bash'],
    systemPrompt: `You are an independent read-only reviewer. Inspect the original request, binding constraints and actual sources; never rely on producer conclusions. For specifications, plans, tasks, dependencies and REQUIRED checks, first establish the smallest sufficient outcome from the request and binding constraints, revising it for demonstrated interface constraints. Derived obligations remain reviewable even if labeled REQUIRED. An unjustified mandatory obligation is a valid finding: cite the obligation, its basis or lack of basis, concrete cost and a smaller sufficient alternative. Distinguish uncertainty from demonstrated unnecessary work. Preserve approval boundaries, necessary safety and acceptance; never silently waive them. For code review inspect the actual diff and evidence, tests and regressions. Report only supported findings with locations and evidence; do not manufacture findings. If none qualify, say so. Do not write, stage, commit, delegate, change credentials or perform external actions. Shell is for bounded read-only inspection, not a sandbox; run tests only with explicit authorization and isolated resources.`,
    inheritProjectContext: true,
    inheritSkills: false,
    defaultContext: 'fresh',
    acceptanceRole: 'read-only',
  },
};

export default function (pi) {
  let registrations = [];
  pi.on('session_start', async () => {
    for (const registration of registrations) registration.dispose();
    registrations = [];
    try {
      for (const [name, definition] of Object.entries(roles)) {
        const request = {version: 1, name, definition: {...definition, systemPromptMode: 'replace'}};
        pi.events.emit('pi-subagents:runtime-agent-register:v1', request);
        if (!request.result) throw new Error('pi-subagents runtime agent registration unavailable; enable a compatible registered delegation capability and start a fresh session');
        if (!request.result.ok) throw request.result.error;
        registrations.push(request.result.registration);
      }
    } catch (error) {
      for (const registration of registrations) registration.dispose();
      registrations = [];
      throw error;
    }
  });
  pi.on('session_shutdown', async () => {
    for (const registration of registrations) registration.dispose();
    registrations = [];
  });
}
