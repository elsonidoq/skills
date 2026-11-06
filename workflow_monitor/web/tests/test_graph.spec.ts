import { test, expect } from '@playwright/test'
import { graphFor, taskTitle, outcomeText, qualificationText, type Occurrence, type Activity, type ChainExecution, type GraphSnapshot } from '../src/graph'
import { layoutNodes } from '../src/layout'

const task = (ref: string, taskId: string | undefined, label: string, prerequisites: string[] = []) => ({ ref, run_ref: 'run', task_id: taskId, label, work_description: `${label} work`, prerequisite_refs: prerequisites })
const call = (ref: string, taskRef: string | null, kind: Activity['invocation_kind'] = 'task_worker', chain = [ref], outcome: Activity['outcome'] = 'unknown'): Activity => ({ ref, run_ref: 'run', invocation_id: ref, occurrence_ref: `${ref}-occ`, task_ref: taskRef, role: kind === 'corrective_worker' ? 'fixing_worker' : 'worker', invocation_kind: kind, outcome, error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: chain, support_ref: null, stopped_by_ref: null, record_refs: [] })
const review = (ref: string, ordinal: number, outcome: ChainExecution['outcome'] = 'unknown', occurrenceRefs: string[] = []): ChainExecution => ({ ref, run_ref: 'run', execution_id: ref, role: 'reviewer', review_ordinal: ordinal, fixing_round: null, outcome, trigger_ref: null, predecessor_ref: null, input_refs: [], occurrence_refs: occurrenceRefs, review_range: { base: null, head: null }, findings: [], commit_refs: {} })
const snapshot = (activities: Activity[] = [], chain: ChainExecution[] = []): GraphSnapshot => ({
  runs: [{ ref: 'run' }], tasks: [task('alpha', 'T003', 'Task', []), task('opaque', undefined, 'Implement dispatch', ['alpha'])],
  review_definitions: [{ ref: 'final', run_ref: 'run', label: 'planned', prerequisite_refs: ['alpha', 'opaque'] }], occurrences: [], records: [], activities, chain
})

test('task titles use meaningful labels or faithful retained excerpts', () => {
  const title = (label: string, work_description?: string | null) => taskTitle({ ...task('a', 'T001', label), work_description })
  expect(title('Task scheduling improvements', 'Other work')).toBe('Task scheduling improvements')
  expect(title('Useful label', null)).toBe('Useful label')
  for (const label of ['', '  ', 'Task', 'Task 12', '123', 'T001', 'abc-12', '123e4567-e89b-12d3-a456-426614174000']) {
    expect(title(label, '  Retained\n  work\ttext  ')).toBe('Retained work text')
    expect(title(label, '  \n ')).toBe('Description unavailable')
    expect(title(label, null)).toBe('Description unavailable')
  }
  expect(title('Task', 'x'.repeat(81))).toBe(`${'x'.repeat(79)}…`)
  expect(title('x'.repeat(81))).toBe(`${'x'.repeat(79)}…`)
  const graph = graphFor(snapshot([call('fix', 'alpha', 'corrective_worker', ['initial', 'fix'])]), [], [])
  expect(graph.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.label).toBe('Task 1 — Worker — Task work')
  expect(graph.nodes.find(node => node.id === 'fix')?.data.label).toBe('Task 1 — Corrective worker — Fix 1 — Task work')
  expect(graph.nodes.find(node => node.id === 'planned-task:run:opaque')?.data.label).toBe('Task 2 — Worker — Implement dispatch')
  const old = { ...snapshot(), runs: [{ ref: 'run', plan_availability: 'unavailable' }], tasks: [], review_definitions: [] }
  expect(graphFor(old, [], []).nodes).toHaveLength(0)
})

test('planned slots persist and reconcile only one exact initial root across lifecycle polls', () => {
  const before = graphFor(snapshot(), [], [])
  const running = graphFor(snapshot([call('initial', 'alpha')]), [], [])
  const returned = graphFor(snapshot([call('initial', 'alpha', 'task_worker', ['initial'], 'returned')]), [], [])
  const failed = graphFor(snapshot([call('initial', 'alpha', 'task_worker', ['initial'], 'failed')]), [], [])
  const ids = ['planned-review:run:final', 'planned-task:run:alpha', 'planned-task:run:opaque']
  for (const graph of [before, running, returned, failed]) expect(graph.nodes.map(node => node.id).sort()).toEqual(ids)
  expect(before.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.status).toContain('planned')
  expect(returned.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.status).toContain('returned')
  expect(failed.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.status).toBe('failed')
  expect(returned.edges.map(edge => [edge.source, edge.target, edge.data?.classification])).toEqual([
    ['planned-task:run:alpha', 'planned-task:run:opaque', 'declared'],
    ['planned-task:run:alpha', 'planned-review:run:final', 'declared'],
    ['planned-task:run:opaque', 'planned-review:run:final', 'declared']
  ])
})

test('exact run/task/kind/chain matching retains resumes, collisions and ambiguity as separate calls', () => {
  // The public boundary replaces private invocation IDs with opaque activity refs.
  const opaqueBoundary = { ...call('activity-root', 'alpha', 'task_worker', ['activity-root'], 'returned'), invocation_id: 'private-invocation', occurrence_ref: 'root-occ' }
  const qualified = graphFor({ ...snapshot([opaqueBoundary]), occurrences: [{ ref: 'root-occ', run_ref: 'run', phase_ref: 'worker', task_ref: 'alpha', role: 'worker', outcome: null, completeness: 'complete', record_refs: [], execution_summary: { state: 'waiting', qualification: 'waiting_for_input' } }], records: [] }, [], [])
  expect(qualified.nodes.map(node => node.id)).not.toContain('activity-root')
  expect(qualified.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.status).toContain('waiting')
  const resumed = call('resume', 'alpha', 'task_worker', ['first', 'resume'], 'returned')
  const corrective = call('fix', 'alpha', 'corrective_worker', ['initial', 'fix'], 'returned')
  const collision = { ...call('other-run', 'alpha', 'task_worker', ['other-run'], 'returned'), run_ref: 'other' }
  const otherTask = call('other-task', 'opaque', 'task_worker', ['other-task'], 'returned')
  const initial = call('initial', 'alpha', 'task_worker', ['initial'], 'returned')
  const graph = graphFor(snapshot([initial, resumed, corrective, collision, otherTask]), [], [])
  expect(graph.nodes.map(node => node.id).sort()).toEqual(['fix', 'other-run', 'planned-review:run:final', 'planned-task:run:alpha', 'planned-task:run:opaque', 'resume'])
  expect(graph.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.identity).toMatchObject({ invocationId: 'initial' })
  expect(graph.nodes.find(node => node.id === 'fix')?.data.label).toContain('Task 1 — Corrective worker — Fix 1')
  expect(graph.nodes.find(node => node.id === 'planned-task:run:opaque')?.data.label).toContain('Task 2 — Worker')

  const ambiguous = graphFor(snapshot([call('root-a', 'alpha'), call('root-b', 'alpha')]), [], [])
  expect(ambiguous.nodes.map(node => node.id)).toContain('root-a')
  expect(ambiguous.nodes.map(node => node.id)).toContain('root-b')
  expect(ambiguous.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.relationQualification).toContain('ambiguous')
  const unproven = graphFor(snapshot([call('resume-only', 'alpha', 'task_worker', ['earlier', 'resume-only'])]), [], [])
  expect(unproven.nodes.find(node => node.id === 'planned-task:run:alpha')?.data.status).toContain('unknown')
  expect(unproven.nodes.map(node => node.id)).toContain('resume-only')
})

test('only exact ordinal-one review replaces initial intent; actual correction calls and qualifications remain distinct', () => {
  const first = review('review-one', 1, 'rejected')
  const second = review('review-two', 2, 'approved')
  const fixOne = call('fix-one', 'alpha', 'corrective_worker', ['initial', 'fix-one'], 'returned')
  const fixTwo = call('fix-two', 'alpha', 'corrective_worker', ['initial', 'fix-two'], 'returned')
  const round: ChainExecution = { ...review('round', 0), role: 'fixer', fixing_round: 1, occurrence_refs: ['fix-one-occ', 'fix-two-occ'] }
  const graph = graphFor(snapshot([fixOne, fixTwo], [first, second, round]), [], [])
  expect(graph.nodes.map(node => node.id).sort()).toEqual(['fix-one', 'fix-two', 'planned-review:run:final', 'planned-task:run:alpha', 'planned-task:run:opaque', 'review-two'])
  expect(graph.nodes.find(node => node.id === 'planned-review:run:final')?.data.status).toContain('changes requested')
  expect(graph.nodes.find(node => node.id === 'review-two')?.data.label).toContain('Review 2')
  expect(graph.nodes.find(node => node.id === 'fix-two')?.data.label).toContain('Fix 2')
  expect(graph.nodes.map(node => node.id)).not.toContain('round')

  const unobserved = { ...call('review-dispatch', null), role: 'reviewer' as const, invocation_id: 'review-one', occurrence_ref: null, invocation_kind: 'unknown' as const }
  const reconciled = graphFor(snapshot([unobserved], [first]), [], [])
  expect(reconciled.nodes.map(node => node.id)).not.toContain('review-dispatch')
  const ambiguous = graphFor(snapshot([], [review('review-a', 1), review('review-b', 1)]), [], [])
  expect(ambiguous.nodes.map(node => node.id)).toEqual(expect.arrayContaining(['review-a', 'review-b', 'planned-review:run:final']))
  expect(ambiguous.nodes.find(node => node.id === 'planned-review:run:final')?.data.relationQualification).toContain('ambiguous')
})

test('all observed calls use qualified lifecycle without successful fallback or raw qualifications', () => {
  const initial = call('initial', 'alpha', 'task_worker', ['initial'], 'returned')
  const correction = { ...call('correction', 'alpha', 'corrective_worker', ['initial', 'correction'], 'returned'), role: 'worker' as const }
  const reviewer = { ...call('review-activity', null), role: 'reviewer' as const, invocation_id: 'private-review', occurrence_ref: 'review-occ' }
  const execution = { ...review('public-review', 2, 'approved', ['review-occ']), execution_id: 'private-review' }
  for (const [state, qualification, css] of [['running', 'recorded_running', 'running'], ['waiting', 'outstanding_input', 'waiting'], ['unknown', 'conflicting_terminal_evidence', 'neutral']] as const) {
    const input = snapshot([initial, correction, reviewer], [execution])
    input.occurrences = [initial, correction, reviewer].map(activity => ({ ref: activity.occurrence_ref!, run_ref: 'run', phase_ref: 'phase', task_ref: activity.task_ref, role: activity.role, outcome: null, completeness: 'complete', record_refs: [], execution_summary: { state, qualification } }))
    const graph = graphFor(input, [], [])
    for (const id of ['planned-task:run:alpha', 'correction', 'public-review']) {
      expect(graph.nodes.find(node => node.id === id)?.className?.split(' ').at(-1)).toBe(css)
      expect(graph.nodes.find(node => node.id === id)?.data.status).toContain(state)
      expect(graph.nodes.find(node => node.id === id)?.data.status).not.toContain(qualification)
    }
    expect(graph.nodes.find(node => node.id === 'correction')?.data.label).toContain('Task 1 — Worker — Correction 1')
    expect(outcomeText(input.occurrences[0], [])).not.toContain(qualification)
  }
  expect(qualificationText('private.schema.value')).toBe('Unknown')
  const stopped = snapshot()
  stopped.occurrences = [{ ref: 'terminal', run_ref: 'run', phase_ref: 'terminal', phase: 'terminal', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [] } as Occurrence]
  expect(graphFor(stopped, [], []).nodes.find(node => node.id === 'planned-review:run:final')?.data.status).toBe('Not started; run stopped')
})

test('declared and recorded relations have different semantics and reject missing or cyclic endpoints', async () => {
  const worker = call('worker', 'alpha', 'task_worker', ['worker'], 'returned')
  const fix = { ...call('fix', 'alpha', 'corrective_worker', ['worker', 'fix'], 'returned'), input_refs: ['worker', 'missing'], trigger_ref: 'worker' }
  const rereview = { ...review('review-two', 2, 'approved'), predecessor_ref: 'review-two' }
  const graph = graphFor(snapshot([worker, fix], [rereview]), [], [])
  const consuming = { ...call('consumer', 'opaque', 'task_worker', ['consumer'], 'returned'), input_refs: ['worker'] }
  const mixed = graphFor(snapshot([worker, consuming]), [], []).edges.find(edge => edge.target === 'planned-task:run:opaque')!
  expect(mixed.data?.classification).toBe('mixed')
  expect(mixed.data?.classifications).toEqual(['declared', 'recorded'])
  expect(mixed.data?.relations).toEqual(['declared-prerequisite', 'recorded-input'])
  expect(mixed.className).toBe('mixed-edge')
  expect(graph.edges.some(edge => edge.data?.classification === 'declared' && edge.data?.relation === 'declared-prerequisite')).toBeTruthy()
  expect(graph.edges.some(edge => edge.data?.classification === 'recorded' && (edge.data?.relations as string[]).includes('recorded-input'))).toBeTruthy()
  expect(graph.nodes.find(node => node.id === 'fix')?.data.relationQualification).toContain('endpoint missing or ambiguous')
  expect(graph.nodes.find(node => node.id === 'review-two')?.data.relationQualification).toContain('self relation rejected')
  expect(graph.nodes.map(node => String(node.data.label)).join(' ')).not.toMatch(/\b(worker|reviewer|task_worker|corrective_worker)_[a-z0-9-]+\b/)
  expect(graph.nodes.every(node => !node.id.startsWith('group:'))).toBeTruthy()
  const layout = await layoutNodes(graph.nodes.map(node => ({ id: node.id, size: { width: node.id === 'fix' ? 260 : 180, height: 70 } })), graph.edges.map(edge => ({ source: edge.source, target: edge.target })))
  expect(layout.elkInput.layoutOptions).toMatchObject({ 'elk.algorithm': 'layered', 'elk.direction': 'DOWN' })
  expect(layout.elkInput.edges.map(edge => [edge.sources[0], edge.targets[0]])).toEqual(graph.edges.map(edge => [edge.source, edge.target]))
  expect(layout.nodes.find(node => node.id === 'fix')).toMatchObject({ width: 260, height: 70 })
})
