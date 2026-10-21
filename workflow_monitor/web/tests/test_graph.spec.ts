import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'
import { graphFor, type GraphSnapshot } from '../src/graph'
import { layoutFootprints, type FootprintLayoutInput } from '../src/layout'

let server: Server
const snapshot = {
  runs: [{ ref: 'run_one', label: '<img src=x onerror=alert(1)> retained failure', completeness: 'recorded', started_at: 1 }, { ref: 'run_two', label: 'Second run', completeness: 'recorded', started_at: 2 }],
  phases: [{ ref: 'phase_one', run_ref: 'run_one', label: 'Worker' }, { ref: 'phase_two', run_ref: 'run_two', label: 'Review' }],
  tasks: [
    { ref: 'task_one', run_ref: 'run_one', label: 'T001', summary: 'First', prerequisite_refs: [], progress: { state: 'completed', qualification: null } },
    { ref: 'task_two', run_ref: 'run_one', label: 'T002', summary: 'Second', prerequisite_refs: ['task_one'], progress: { state: 'running', qualification: null } },
    { ref: 'task_three', run_ref: 'run_one', label: 'T003', summary: 'Pending', prerequisite_refs: [], progress: { state: 'pending', qualification: null } }
  ],
  review_definitions: [{ ref: 'review_definition', run_ref: 'run_one', label: 'Planned independent review — not an agent call.' }],
  occurrences: [{ ref: 'occ_failed', run_ref: 'run_one', phase_ref: 'phase_one', task_ref: null, role: 'worker', outcome: 'failed', completeness: 'complete', record_refs: ['record_one'] }, { ref: 'occ_reviewer', run_ref: 'run_two', phase_ref: 'phase_two', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: ['record_two'] }],
  records: [{ ref: 'record_one', run_ref: 'run_one', occurrence_ref: 'occ_failed', kind: 'failed', source_seq: 1, recorded_at: 1, exit_code: 1, finding_count: null, review_base: null, review_head: null }, { ref: 'record_two', run_ref: 'run_two', occurrence_ref: 'occ_reviewer', kind: 'passed', source_seq: 2, recorded_at: 2, exit_code: null, finding_count: 0, review_base: 'a'.repeat(40), review_head: 'b'.repeat(40) }],
  edges: [{ ref: 'edge_one', run_ref: 'run_one', type: 'phase_occurrence', from_ref: 'phase_one', to_ref: 'occ_failed', resolution: 'recorded' }, { ref: 'edge_two', run_ref: 'run_one', type: 'execution_milestone', from_ref: 'occ_failed', to_ref: 'record_one', resolution: 'recorded' }, { ref: 'edge_three', run_ref: 'run_two', type: 'phase_occurrence', from_ref: 'phase_two', to_ref: 'occ_reviewer', resolution: 'recorded' }],
  inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, hidden_count: 0 }
}

test('actual activity projection retains only explicit calls and relations', () => {
  const root: GraphSnapshot = {
    runs: [{ ref: 'run' }],
    tasks: [{ ref: 'plan-only', run_ref: 'run', task_id: 'P001', label: 'Planned only', summary: 'must not render', prerequisite_refs: [] }],
    review_definitions: [{ ref: 'declared-review', run_ref: 'run', label: 'must not render' }], records: [],
    occurrences: [
      { ref: 'occ_a', run_ref: 'run', phase_ref: 'worker', task_ref: null, role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'occ_b', run_ref: 'run', phase_ref: 'worker', task_ref: null, role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'ambiguous', run_ref: 'run', phase_ref: 'worker', task_ref: null, role: 'worker', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'stop', run_ref: 'run', phase_ref: 'terminal', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'ambiguous' }
    ],
    activities: [
      { ref: 'call_a', run_ref: 'run', invocation_id: 'a', occurrence_ref: 'occ_a', task_ref: null, role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: ['call_a'], support_ref: null, stopped_by_ref: null, record_refs: [] },
      { ref: 'call_b', run_ref: 'run', invocation_id: 'b', occurrence_ref: 'occ_b', task_ref: null, role: 'fixing_worker', invocation_kind: 'corrective_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['call_a'], correction_chain: ['call_a', 'call_b'], support_ref: null, stopped_by_ref: null, record_refs: [] },
      { ref: 'call_ambiguous', run_ref: 'run', invocation_id: 'ambiguous', occurrence_ref: 'ambiguous', task_ref: null, role: 'worker', invocation_kind: 'task_worker', outcome: 'failed', error_category: 'check', input_qualification: 'unknown', input_refs: ['missing'], correction_chain: ['call_ambiguous', 'missing'], support_ref: null, stopped_by_ref: 'call_ambiguous', record_refs: [] }
    ],
    chain: [
      { ref: 'review_one', run_ref: 'run', execution_id: 'review-1', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: 'review_two', occurrence_refs: ['ambiguous'], review_range: { base: null, head: null }, findings: [], commit_refs: {} },
      { ref: 'review_two', run_ref: 'run', execution_id: 'review-2', role: 'reviewer', review_ordinal: 2, fixing_round: null, outcome: 'approved', trigger_ref: null, predecessor_ref: 'review_one', occurrence_refs: ['ambiguous'], review_range: { base: null, head: null }, findings: [], commit_refs: {} }
    ]
  }
  const graph = graphFor(root, [], [])
  expect(graph.nodes.map(node => node.id).sort()).toEqual(['call_a', 'call_ambiguous', 'call_b', 'review_one', 'review_two', 'stop'])
  expect(graph.nodes.find(node => node.id === 'plan-only')).toBeUndefined()
  expect(graph.nodes.find(node => node.id === 'declared-review')).toBeUndefined()
  const joined = graph.edges.find(edge => edge.source === 'call_a' && edge.target === 'call_b')
  expect(joined?.data).toMatchObject({ relations: ['recorded-input', 'recorded-correction'] })
  expect(graph.edges.find(edge => edge.id === 'stop_stop')).toMatchObject({ source: 'call_ambiguous', target: 'stop', data: { relation: 'recorded-stop-support' } })
  expect(graph.edges.find(edge => edge.source === 'review_two' && edge.target === 'review_one')).toMatchObject({ data: { relation: 'recorded-correction-predecessor' } })
  expect(graph.edges.find(edge => edge.source === 'review_one' && edge.target === 'review_two')).toBeUndefined()
  expect(graph.nodes.find(node => node.id === 'review_two')?.data.relationQualification).toContain('cyclic relation rejected')
  expect(graph.edges.some(edge => edge.source === 'missing' || edge.target === 'missing')).toBeFalsy()
  expect(graph.nodes.find(node => node.id === 'call_ambiguous')?.data.relationQualification).toContain('endpoint missing or ambiguous')
})

test('readable backbone projection preserves declared topology and recorded ownership', () => {
  const root: GraphSnapshot = {
    runs: [{ ref: 'run_readable', plan_availability: 'complete' }],
    tasks: [
      { ref: 'task_a', run_ref: 'run_readable', task_id: 'T001', label: 'Task', summary: 'Design branch', prerequisite_refs: [], progress: { state: 'pending', qualification: null } },
      { ref: 'task_b', run_ref: 'run_readable', task_id: 'T002', label: 'Task', summary: 'Implement branch', prerequisite_refs: ['task_a'], progress: { state: 'running', qualification: null } },
      { ref: 'task_c', run_ref: 'run_readable', task_id: 'T003', label: 'Task', summary: 'Review branch', prerequisite_refs: ['task_a'], progress: { state: 'returned', qualification: null } },
      { ref: 'task_d', run_ref: 'run_readable', task_id: 'T004', label: 'Join work', summary: 'Join summary', prerequisite_refs: ['task_a', 'task_b', 'task_c'], progress: { state: 'pending', qualification: null } },
      { ref: 'task_pending', run_ref: 'run_readable', label: 'Task', summary: 'Independent pending work', prerequisite_refs: [], progress: { state: 'pending', qualification: null } }
    ],
    review_definitions: [{ ref: 'review_plan', run_ref: 'run_readable', label: 'Planned independent review — not an agent call' }],
    occurrences: [
      { ref: 'attempt_a', occurrence_id: '1', run_ref: 'run_readable', phase_ref: 'phase', task_ref: 'task_a', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'attempt_b', occurrence_id: '2', run_ref: 'run_readable', phase_ref: 'phase', task_ref: 'task_b', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'fix_b', occurrence_id: '3', run_ref: 'run_readable', phase_ref: 'phase', task_ref: 'task_b', role: 'fixing_worker', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'unknown_attempt', run_ref: 'run_readable', phase_ref: 'phase', task_ref: null, role: 'reviewer', outcome: null, completeness: 'incomplete', record_refs: [] },
      { ref: 'dangling_attempt', run_ref: 'run_readable', phase_ref: 'phase', task_ref: 'missing_task', role: 'worker', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'other_run_attempt', occurrence_id: '9', run_ref: 'other_run', phase_ref: 'phase', task_ref: 'task_b', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] }
    ],
    records: [],
    chain: [
      { ref: 'chain_b', run_ref: 'run_readable', execution_id: 'execution-unrelated-to-task', role: 'fixer', review_ordinal: null, fixing_round: 2, outcome: 'failed', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['attempt_b', 'fix_b'], review_range: { base: null, head: null }, findings: [], commit_refs: {} },
      { ref: 'chain_conflict', run_ref: 'run_readable', execution_id: 'task_a-looking-id', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['attempt_a', 'attempt_b'], review_range: { base: null, head: null }, findings: [], commit_refs: {} },
      { ref: 'chain_missing', run_ref: 'run_readable', execution_id: 'task_d', role: 'unknown', review_ordinal: null, fixing_round: null, outcome: 'unknown', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['not_loaded'], review_range: { base: null, head: null }, findings: [], commit_refs: {} }
    ]
  }
  const relations = [{ run_ref: 'run_readable', source_run_ref: 'run_readable', review_occurrence_ref: 'unknown_attempt', resolution: 'resolved' }]
  const initial = graphFor(root, [], relations)
  const dependencies = initial.edges.filter(edge => edge.data?.relation === 'declared-prerequisite')
  expect(dependencies.map(edge => [edge.id, edge.source, edge.target]).sort()).toEqual([
    ['dependency_task_a_task_b', 'task_a', 'task_b'],
    ['dependency_task_a_task_c', 'task_a', 'task_c'],
    ['dependency_task_a_task_d', 'task_a', 'task_d'],
    ['dependency_task_b_task_d', 'task_b', 'task_d'],
    ['dependency_task_c_task_d', 'task_c', 'task_d']
  ])
  expect(initial.nodes.filter(node => node.className?.includes('planned-node')).map(node => node.id).sort()).toEqual(['task_a', 'task_b', 'task_c', 'task_d', 'task_pending'])
  expect(initial.edges.some(edge => edge.id.startsWith('attachment_') || edge.id.startsWith('sequence_'))).toBeFalsy()
  expect(initial.edges.find(edge => edge.id === 'followup_unknown_attempt_chain_b')).toMatchObject({ data: { classification: 'secondary', qualification: 'declared cross-run correction; not recorded exact execution causality' } })
  expect(dependencies.every(edge => edge.label == null && edge.data?.relation === 'declared-prerequisite')).toBeTruthy()
  expect(initial.nodes.find(node => node.id === 'task_a')?.data).toMatchObject({ label: 'Design branch', taskCode: 'T001' })
  expect(initial.nodes.find(node => node.id === 'task_pending')?.data).toMatchObject({ label: 'Independent pending work', taskCode: 'Unknown task ID' })
  expect(initial.nodes.find(node => node.id === 'review_plan')?.data).toMatchObject({ identity: { kind: 'planned-review-definition' }, owner: null })
  expect(initial.nodes.find(node => node.id === 'chain_b')?.data).toMatchObject({ owner: 'task_b', label: 'Fixing agent round 2' })
  expect(initial.nodes.find(node => node.id === 'chain_conflict')?.data).toMatchObject({ owner: { scope: 'run', runRef: 'run_readable', state: 'unassigned' } })
  expect(initial.nodes.find(node => node.id === 'chain_missing')?.data).toMatchObject({ owner: { scope: 'run', runRef: 'run_readable', state: 'unassigned' } })
  expect(initial.nodes.find(node => node.id === 'unknown_attempt')?.data).toMatchObject({ owner: { scope: 'run', state: 'unassigned' } })
  expect(initial.nodes.find(node => node.id === 'dangling_attempt')?.data).toMatchObject({ owner: { scope: 'run', state: 'unassigned' } })
  expect(initial.nodes.find(node => node.id === 'other_run_attempt')?.data).toMatchObject({ owner: { scope: 'run', runRef: 'other_run', state: 'unassigned' } })
  expect(initial.nodes.find(node => node.id === 'attempt_b')).toBeUndefined()
  expect(initial.nodes.find(node => node.id === 'fix_b')).toBeUndefined()
  expect(initial.nodes.find(node => node.id === 'unknown_attempt')?.data.label).toContain('Reviewer attempt unknown')

  for (const state of ['pending', 'running', 'returned', 'checkpoint', 'failed']) {
    const transitioned = graphFor({ ...root, tasks: root.tasks.map(task => task.ref === 'task_b' ? { ...task, progress: { state, qualification: null } } : task) }, [], relations)
    expect(transitioned.topology).toBe(initial.topology)
    expect(transitioned.nodes.find(node => node.id === 'task_b')?.data.status).toBe(`Plan progress: ${state}`)
  }
})

test('readable state relations retain only qualified recorded stops and corrections', () => {
  const root: GraphSnapshot = {
    runs: [{ ref: 'original', plan_availability: 'complete' }], tasks: [], review_definitions: [], records: [],
    occurrences: [
      { ref: 'returned_worker', occurrence_id: '1', run_ref: 'original', phase_ref: 'work', task_ref: null, role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [], execution_summary: { state: 'success', qualification: null } },
      { ref: 'current_stop', run_ref: 'original', phase_ref: 'check', task_ref: null, role: 'check', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'returned_worker' },
      { ref: 'before_agent_stop', run_ref: 'original', phase_ref: 'prepare', task_ref: null, role: 'prepare', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: null },
      { ref: 'recovered_check', run_ref: 'original', phase_ref: 'check', task_ref: null, role: 'check', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'review_occurrence', run_ref: 'original', phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'returned_worker' }
    ],
    chain: [{ ref: 'review_execution', run_ref: 'original', execution_id: 'review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['review_occurrence'], review_range: { base: null, head: null }, findings: ['recorded rejection'], commit_refs: {} }]
  }
  const correction: GraphSnapshot = {
    runs: [{ ref: 'correction' }], tasks: [], records: [],
    occurrences: [
      { ref: 'correction_review_occurrence', run_ref: 'correction', phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'fix_occurrence', run_ref: 'correction', phase_ref: 'work', task_ref: null, role: 'fixing_worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'check_occurrence', run_ref: 'correction', phase_ref: 'check', task_ref: null, role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['check_record'] },
      { ref: 'checkpoint_occurrence', run_ref: 'correction', phase_ref: 'checkpoint', task_ref: null, role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['checkpoint_record'] }
    ],
    edges: [
      { ref: 'trigger_edge', run_ref: 'correction', type: 'chain_trigger', from_ref: 'correction_review_execution', to_ref: 'fix_execution', resolution: 'recorded' },
      { ref: 'predecessor_edge', run_ref: 'correction', type: 'chain_predecessor', from_ref: 'fix_execution', to_ref: 'rereview_execution', resolution: 'recorded' },
      { ref: 'check_edge', run_ref: 'correction', type: 'chain_check', from_ref: 'fix_execution', to_ref: 'check_record', resolution: 'recorded' },
      { ref: 'checkpoint_edge', run_ref: 'correction', type: 'chain_checkpoint', from_ref: 'fix_execution', to_ref: 'checkpoint_record', resolution: 'recorded' },
      { ref: 'represented_support_edge', run_ref: 'correction', type: 'chain_check', from_ref: 'fix_execution', to_ref: 'correction_review_occurrence', resolution: 'recorded' }
    ],
    chain: [
      { ref: 'correction_review_execution', run_ref: 'correction', execution_id: 'correction-review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['correction_review_occurrence'], review_range: { base: null, head: null }, findings: ['still distinct'], commit_refs: {} },
      { ref: 'fix_execution', run_ref: 'correction', execution_id: 'fix', role: 'fixer', review_ordinal: null, fixing_round: 1, outcome: 'approved', trigger_ref: 'correction_review_execution', predecessor_ref: null, occurrence_refs: ['fix_occurrence'], review_range: { base: null, head: null }, findings: [], commit_refs: {} }
    ]
  }
  const graph = graphFor(root, [correction], [
    { run_ref: 'correction', source_run_ref: 'original', review_occurrence_ref: 'review_occurrence', resolution: 'resolved' },
    { run_ref: 'missing', source_run_ref: 'original', review_occurrence_ref: 'review_occurrence', resolution: 'unresolved' },
    { run_ref: 'correction', source_run_ref: 'original', review_occurrence_ref: 'missing_review', resolution: 'cyclic' }
  ])
  const edge = (id: string) => graph.edges.find(item => item.id === id)
  expect(graph.nodes.find(node => node.id === 'returned_worker')?.className).toContain('success')
  expect(graph.nodes.find(node => node.id === 'current_stop')?.className).toContain('failed')
  expect(graph.nodes.find(node => node.id === 'recovered_check')).toBeUndefined()
  expect(edge('stop_current_stop')).toMatchObject({ source: 'returned_worker', target: 'current_stop', data: { classification: 'secondary', relation: 'recorded-stop-support' } })
  expect(edge('stop_review_occurrence')).toMatchObject({ source: 'returned_worker', target: 'review_execution', data: { classification: 'secondary', relation: 'recorded-stop-support' } })
  expect(graph.nodes.find(node => node.id === 'review_occurrence')).toBeUndefined()
  expect(graph.edges.some(item => item.target === 'before_agent_stop')).toBeFalsy()
  expect(graph.nodes.find(node => node.id === 'before_agent_stop')).toBeDefined()
  expect(edge('trigger_edge')).toMatchObject({ source: 'correction_review_execution', target: 'fix_execution', data: { classification: 'secondary', relation: 'chain_trigger' } })
  expect(edge('check_edge')).toMatchObject({ source: 'fix_execution', target: 'check_occurrence', data: { identity: { ref: 'check_edge', toRef: 'check_occurrence' } } })
  expect(edge('checkpoint_edge')).toMatchObject({ source: 'fix_execution', target: 'checkpoint_occurrence', data: { identity: { ref: 'checkpoint_edge', toRef: 'checkpoint_occurrence' } } })
  expect(edge('represented_support_edge')).toMatchObject({ source: 'fix_execution', target: 'correction_review_execution', data: { identity: { ref: 'represented_support_edge', toRef: 'correction_review_occurrence' } } })
  expect(graph.nodes.find(node => node.id === 'correction_review_occurrence')).toBeUndefined()
  expect(edge('predecessor_edge')).toBeUndefined()
  expect(edge('followup_review_occurrence_fix_execution')).toMatchObject({ source: 'review_execution', target: 'fix_execution', data: { classification: 'secondary', relation: 'declared-cross-run-correction', qualification: 'declared cross-run correction; not recorded exact execution causality' } })
  expect(graph.edges.some(item => item.id.includes('missing') || item.data?.resolution === 'unresolved' || item.data?.resolution === 'cyclic')).toBeFalsy()
  expect(graph.edges.filter(item => item.data?.classification === 'backbone')).toEqual([])
  expect(graph.edges.every(item => item.data?.classification === 'secondary')).toBeTruthy()
})

test('readable footprint layout uses DOWN prerequisite footprints and preserves contained members', async () => {
  const input: FootprintLayoutInput = {
    groups: [
      { id: 'task_a', kind: 'task', header: { width: 160, height: 32 }, members: [{ id: 'attempt_a', size: { width: 130, height: 48 } }] },
      { id: 'task_b', kind: 'task', header: { width: 220, height: 44 }, members: [{ id: 'attempt_b_1', size: { width: 140, height: 38 } }, { id: 'attempt_b_2', size: { width: 180, height: 64 } }] },
      { id: 'task_c', kind: 'task', header: { width: 130, height: 28 }, members: [] },
      { id: 'task_d', kind: 'task', header: { width: 190, height: 36 }, members: [{ id: 'attempt_d', size: { width: 210, height: 40 } }] },
      { id: 'task_pending', kind: 'task', header: { width: 150, height: 30 }, members: [] },
      { id: 'run_review', kind: 'run-review', header: { width: 170, height: 34 }, members: [{ id: 'review_execution', size: { width: 150, height: 52 } }] },
      { id: 'unassigned_history', kind: 'unassigned', header: { width: 175, height: 34 }, members: [{ id: 'unknown_attempt', size: { width: 165, height: 46 } }] }
    ],
    prerequisites: [
      { source: 'task_a', target: 'task_b' },
      { source: 'task_a', target: 'task_c' },
      { source: 'task_a', target: 'task_d' },
      { source: 'task_b', target: 'task_d' },
      { source: 'task_c', target: 'task_d' }
    ],
    secondaryRelations: [{ source: 'review_execution', target: 'attempt_b_2' }]
  }
  const layout = await layoutFootprints(input)
  expect(layout.elkInput.layoutOptions).toMatchObject({ 'elk.algorithm': 'layered', 'elk.direction': 'DOWN' })
  expect(layout.elkInput.edges.map(edge => [edge.sources[0], edge.targets[0]])).toEqual(input.prerequisites.map(edge => [edge.source, edge.target]))
  expect(layout.groups.map(group => group.id)).toEqual(input.groups.map(group => group.id))
  const byId = new Map(layout.groups.map(group => [group.id, group]))
  const contains = (outer: { x: number; y: number; width: number; height: number }, inner: { x: number; y: number; width: number; height: number }) =>
    inner.x >= outer.x && inner.y >= outer.y && inner.x + inner.width <= outer.x + outer.width && inner.y + inner.height <= outer.y + outer.height
  for (const group of layout.groups) {
    expect(contains(group.bounds, group.header)).toBeTruthy()
    for (const child of group.children) expect(contains(group.bounds, child.bounds)).toBeTruthy()
  }
  for (const prerequisite of input.prerequisites) {
    const source = byId.get(prerequisite.source)!.bounds
    const target = byId.get(prerequisite.target)!.bounds
    expect(target.y).toBeGreaterThanOrEqual(source.y + source.height)
  }
  expect(byId.get('unassigned_history')).toMatchObject({ kind: 'unassigned', children: [{ id: 'unknown_attempt' }] })

  const withoutSecondary = await layoutFootprints({ ...input, secondaryRelations: [] })
  expect(withoutSecondary.groups.filter(group => group.kind === 'task')).toEqual(layout.groups.filter(group => group.kind === 'task'))
  const enlarged = await layoutFootprints({
    ...input,
    groups: input.groups.map(group => group.id === 'task_b'
      ? { ...group, header: { width: 280, height: 70 }, members: [...group.members, { id: 'attempt_b_3', size: { width: 240, height: 80 } }] }
      : group)
  })
  expect(enlarged.groups.find(group => group.id === 'task_b')!.bounds.width).toBeGreaterThan(byId.get('task_b')!.bounds.width)
  expect(enlarged.groups.find(group => group.id === 'task_b')!.bounds.height).toBeGreaterThan(byId.get('task_b')!.bounds.height)
})

function selected(run: string) {
  return { ...snapshot, runs: snapshot.runs.filter(item => item.ref === run).map(item => ({ ...item, plan_availability: run === 'run_one' ? 'complete' : 'unavailable' })), phases: snapshot.phases.filter(item => item.run_ref === run), tasks: snapshot.tasks.filter(item => item.run_ref === run), review_definitions: snapshot.review_definitions.filter(item => item.run_ref === run), occurrences: snapshot.occurrences.filter(item => item.run_ref === run), records: snapshot.records.filter(item => item.run_ref === run), edges: snapshot.edges.filter(item => item.run_ref === run), inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, hidden_count: 0 } }
}

test.beforeAll(async () => {
  server = createServer(async (request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: snapshot.runs })); return }
    const match = url.pathname.match(/^\/api\/monitor\/v1\/runs\/(run_(?:one|two))\/snapshot$/)
    if (match) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(selected(match[1]))); return }
    const relative = normalize(url.pathname === '/' ? 'index.html' : url.pathname.slice(1)).replace(/^\.\.(?:[/\\]|$)/, '')
    try {
      const content = await readFile(join('dist', relative))
      const types: Record<string, string> = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }
      response.setHeader('content-type', types[extname(relative)] ?? 'application/octet-stream')
      response.end(content)
    } catch { response.statusCode = 404; response.end() }
  })
  await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve))
})

test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))

test('switches selected production graph, selects details, and provides graph controls', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('button', { name: /retained failure/ })).toBeVisible()
  await expect(page.locator('img')).toHaveCount(0)
  await expect(page.locator('.planned-node')).toHaveCount(3)
  await expect(page.locator('.planned-review-node')).toHaveCount(1)
  await expect(page.locator('.react-flow__edge.dependency-edge')).toHaveCount(1)
  await expect(page.locator('.planned-review-node')).toContainText('Planned independent review — not an agent call.')
  await page.locator('.react-flow__node[data-id="occ_failed"]').click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Execution outcome: failed')
  await page.getByRole('button', { name: /Second run/ }).click()
  await expect(page.locator('.react-flow__node[data-id="occ_reviewer"]')).toBeVisible()
  await expect(page.getByText('Complete graph unavailable')).toBeVisible()
  await page.getByTitle('Zoom In').click()
  await expect(page.getByText('Inventory: 1 records, 1 occurrences, 1 phases; 0 hidden.')).toBeVisible()
})

test('updates the controlled viewport while background panning is held', async ({ page }) => {
  await page.goto('/')
  const pane = page.locator('.react-flow__pane')
  await expect(pane).toBeVisible()
  // Wait for the initial fit effect before capturing the user-controlled viewport.
  await page.waitForTimeout(250)
  const before = await page.locator('.react-flow__viewport').evaluate(element => element.style.transform)
  const box = await pane.boundingBox()
  if (!box) throw new Error('Graph pane has no bounds.')

  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down()
  await page.mouse.move(box.x + box.width / 2 - 150, box.y + box.height / 2 - 100)
  // A controlled graph must retain the moved transform while the pointer remains down,
  // rather than only committing the internal transform from onMoveEnd on release.
  await page.waitForTimeout(100)
  const whileHeld = await page.locator('.react-flow__viewport').evaluate(element => element.style.transform)
  expect(whileHeld).not.toBe(before)
  await page.mouse.up()
  await expect.poll(() => page.locator('.react-flow__viewport').evaluate(element => element.style.transform)).toBe(whileHeld)
})

test('keeps inner nodes and connectors visible throughout background movement', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.planned-node')).toHaveCount(3)
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(1)
  await page.waitForTimeout(250)
  const start = await page.evaluate(() => {
    const pane = document.querySelector('.react-flow__pane')!
    const bounds = pane.getBoundingClientRect()
    for (let y = bounds.top + 20; y < bounds.bottom - 20; y += 20) {
      for (let x = bounds.left + 20; x < bounds.right - 20; x += 20) {
        if (document.elementFromPoint(x, y) === pane) return { x, y }
      }
    }
    throw new Error('No blank graph pane point available for background pan.')
  })
  await page.evaluate(() => {
    const failures: string[] = []
    ;(window as Window & { panVisibilityFailures?: string[] }).panVisibilityFailures = failures
    // End-of-frame geometry misses nodes hidden and remeasured within the same frame.
    // Retain both sides of style mutations and edge removals, not just the final DOM.
    const observer = new MutationObserver(records => {
      for (const record of records) {
        if (record.type === 'attributes' && record.target instanceof HTMLElement && record.target.matches('.react-flow__node:not(.owner-group)')) {
          if (record.oldValue?.includes('visibility: hidden') || record.target.style.visibility === 'hidden') failures.push(`hidden node: ${record.target.dataset.id}`)
        }
        for (const removed of record.removedNodes) {
          if (removed instanceof Element && (removed.matches('.react-flow__edge') || removed.querySelector('.react-flow__edge'))) failures.push('removed connector')
        }
      }
    })
    observer.observe(document.querySelector('.react-flow__viewport')!, { subtree: true, attributes: true, attributeFilter: ['style'], attributeOldValue: true, childList: true })
  })
  await page.mouse.move(start.x, start.y)
  await page.mouse.down()
  for (let step = 1; step <= 8; step++) {
    await page.mouse.move(start.x + step * 4, start.y + step * 3)
    const visible = await page.evaluate(() => {
      const nodes = [...document.querySelectorAll<HTMLElement>('.react-flow__node:not(.owner-group)')]
      const edges = [...document.querySelectorAll<SVGElement>('.react-flow__edge-path')]
      return nodes.length > 0 && edges.length === 1 && [...nodes, ...edges].every(element => {
        const style = getComputedStyle(element)
        const bounds = element.getBoundingClientRect()
        const hasGeometry = element instanceof SVGPathElement ? element.getTotalLength() > 0 : bounds.width > 0 && bounds.height > 0
        return style.visibility === 'visible' && style.display !== 'none' && style.opacity !== '0' && hasGeometry
      })
    })
    expect(visible).toBe(true)
  }
  const failures = await page.evaluate(() => (window as Window & { panVisibilityFailures?: string[] }).panVisibilityFailures)
  await page.mouse.up()
  expect(failures).toEqual([])
})
