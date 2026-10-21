import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'
import { graphFor, type GraphSnapshot } from '../src/graph'

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
      { ref: 'review_occurrence', run_ref: 'original', phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [] }
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
      { ref: 'checkpoint_edge', run_ref: 'correction', type: 'chain_checkpoint', from_ref: 'fix_execution', to_ref: 'checkpoint_record', resolution: 'recorded' }
    ],
    chain: [
      { ref: 'correction_review_execution', run_ref: 'correction', execution_id: 'correction-review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['correction_review_occurrence'], review_range: { base: null, head: null }, findings: ['still distinct'], commit_refs: {} },
      { ref: 'fix_execution', run_ref: 'correction', execution_id: 'fix', role: 'fixer', review_ordinal: null, fixing_round: 1, outcome: 'approved', trigger_ref: 'correction_review_execution', predecessor_ref: null, occurrence_refs: ['fix_occurrence'], review_range: { base: null, head: null }, findings: [], commit_refs: {} }
    ]
  }
  const graph = graphFor(root, [correction], [
    { run_ref: 'correction', source_run_ref: 'original', review_occurrence_ref: 'review_execution', resolution: 'resolved' },
    { run_ref: 'missing', source_run_ref: 'original', review_occurrence_ref: 'review_execution', resolution: 'unresolved' },
    { run_ref: 'correction', source_run_ref: 'original', review_occurrence_ref: 'missing_review', resolution: 'cyclic' }
  ])
  const edge = (id: string) => graph.edges.find(item => item.id === id)
  expect(graph.nodes.find(node => node.id === 'returned_worker')?.className).toContain('success')
  expect(graph.nodes.find(node => node.id === 'current_stop')?.className).toContain('failed')
  expect(graph.nodes.find(node => node.id === 'recovered_check')).toBeUndefined()
  expect(edge('stop_current_stop')).toMatchObject({ source: 'returned_worker', target: 'current_stop', data: { classification: 'secondary', relation: 'recorded-stop-support' } })
  expect(graph.edges.some(item => item.target === 'before_agent_stop')).toBeFalsy()
  expect(graph.nodes.find(node => node.id === 'before_agent_stop')).toBeDefined()
  expect(edge('trigger_edge')).toMatchObject({ source: 'correction_review_execution', target: 'fix_execution', data: { classification: 'secondary', relation: 'chain_trigger' } })
  expect(edge('check_edge')).toMatchObject({ source: 'fix_execution', target: 'check_occurrence', data: { identity: { ref: 'check_edge', toRef: 'check_occurrence' } } })
  expect(edge('checkpoint_edge')).toMatchObject({ source: 'fix_execution', target: 'checkpoint_occurrence', data: { identity: { ref: 'checkpoint_edge', toRef: 'checkpoint_occurrence' } } })
  expect(edge('predecessor_edge')).toBeUndefined()
  expect(edge('followup_review_execution_fix_execution')).toMatchObject({ source: 'review_execution', target: 'fix_execution', data: { classification: 'secondary', relation: 'declared-cross-run-correction', qualification: 'declared cross-run correction; not recorded exact execution causality' } })
  expect(graph.edges.some(item => item.id.includes('missing') || item.data?.resolution === 'unresolved' || item.data?.resolution === 'cyclic')).toBeFalsy()
  expect(graph.edges.filter(item => item.data?.classification === 'backbone')).toEqual([])
  expect(graph.edges.every(item => item.data?.classification === 'secondary')).toBeTruthy()
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
