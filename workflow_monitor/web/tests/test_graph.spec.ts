import { test, expect } from '@playwright/test'
import { graphFor, type GraphSnapshot } from '../src/graph'
import { layoutNodes } from '../src/layout'

test('actual activity projection: projects calls and lays measured boxes DOWN using only validated edges', async () => {
  const snapshot: GraphSnapshot = {
    runs: [{ ref: 'run' }], tasks: [{ ref: 'task', run_ref: 'run', task_id: 'T005', label: 'Task', summary: 'Render activity', prerequisite_refs: [] }], records: [],
    occurrences: [{ ref: 'stop', run_ref: 'run', phase_ref: 'stop', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'fix' }],
    activities: [
      { ref: 'worker', run_ref: 'run', invocation_id: 'worker', occurrence_ref: 'worker-occ', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: ['worker'], support_ref: null, stopped_by_ref: null, record_refs: [] },
      { ref: 'fix', run_ref: 'run', invocation_id: 'fix', occurrence_ref: 'fix-occ', task_ref: 'task', role: 'fixing_worker', invocation_kind: 'corrective_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['worker'], correction_chain: ['worker', 'fix'], support_ref: null, stopped_by_ref: null, record_refs: [] }
    ],
    chain: [{ ref: 'review', run_ref: 'run', execution_id: 'review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: 'worker', predecessor_ref: null, occurrence_refs: [], review_range: { base: null, head: null }, findings: [], commit_refs: {} }]
  }
  const graph = graphFor(snapshot, [], [])
  expect(graph.nodes.map(node => node.id).sort()).toEqual(['fix', 'review', 'stop', 'worker'])
  expect(graph.nodes.every(node => !node.id.startsWith('group:'))).toBeTruthy()
  const layout = await layoutNodes(graph.nodes.map(node => ({ id: node.id, size: { width: node.id === 'fix' ? 260 : 180, height: 70 } })), graph.edges.map(edge => ({ source: edge.source, target: edge.target })))
  expect(layout.elkInput.layoutOptions).toMatchObject({ 'elk.algorithm': 'layered', 'elk.direction': 'DOWN' })
  expect(layout.elkInput.edges.map(edge => [edge.sources[0], edge.targets[0]])).toEqual(graph.edges.map(edge => [edge.source, edge.target]))
  expect(layout.nodes.find(node => node.id === 'fix')).toMatchObject({ width: 260, height: 70 })
  expect(layout.nodes.find(node => node.id === 'fix')!.y).toBeGreaterThanOrEqual(layout.nodes.find(node => node.id === 'worker')!.y + 70)
})
