import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { createServer as createViteServer, type ViteDevServer } from 'vite'

let server: Server
let vite: ViteDevServer
let reads = 0
const sha = (value: string) => value.repeat(40)
const run = { ref: 'run_chain', display_id: 'chain-fixture', label: 'Synthetic recorded chain', completeness: 'recorded', started_at: 1, plan_availability: 'complete' }
const tasks = [
  { ref: 'task_a', run_ref: run.ref, task_id: 'A', label: 'A', summary: 'Synthetic branch root', prerequisite_refs: [], progress: { state: 'completed', qualification: null } },
  { ref: 'task_b', run_ref: run.ref, task_id: 'B', label: 'B', summary: 'Synthetic branch', prerequisite_refs: ['task_a'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_c', run_ref: run.ref, task_id: 'C', label: 'C', summary: 'Synthetic branch', prerequisite_refs: ['task_a'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_d', run_ref: run.ref, task_id: 'D', label: 'D', summary: 'Synthetic branch leaf', prerequisite_refs: ['task_b', 'task_c'], progress: { state: 'completed', qualification: null } },
]
const chain = [
  { ref: 'review_one', run_ref: run.ref, execution_id: 'review_one', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['occ_review_one'], review_range: { base: sha('a'), head: sha('b') }, findings: ['src/example.ts:7 - synthetic rejection'], commit_refs: { base: sha('a'), head: sha('b') } },
  { ref: 'fix_one', run_ref: run.ref, execution_id: 'fix_one', role: 'fixer', review_ordinal: null, fixing_round: 1, outcome: 'approved', trigger_ref: 'review_one', predecessor_ref: 'review_one', occurrence_refs: ['occ_fix'], review_range: { base: sha('a'), head: sha('c') }, findings: [], commit_refs: { commit: sha('c') } },
  { ref: 'review_two', run_ref: run.ref, execution_id: 'review_two', role: 'reviewer', review_ordinal: 2, fixing_round: null, outcome: 'approved', trigger_ref: null, predecessor_ref: 'fix_one', occurrence_refs: ['occ_review_two'], review_range: { base: sha('a'), head: sha('c') }, findings: [], commit_refs: { head: sha('c') } },
]
function snapshot() {
  reads++
  const rereview = reads > 1 ? { ...chain[2], outcome: 'rejected' as const, findings: ['src/example.ts:9 - status refresh'] } : chain[2]
  return {
    runs: [run], phases: [], tasks, review_definitions: [], chain: [chain[0], chain[1], rereview], chain_acceptance: {},
    occurrences: [
      { ref: 'worker_a', run_ref: run.ref, phase_ref: 'worker', task_ref: 'task_a', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'occ_review_one', run_ref: run.ref, phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'occ_fix', run_ref: run.ref, phase_ref: 'worker', task_ref: 'task_d', role: 'fixing_worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'fix_check', run_ref: run.ref, phase_ref: 'check', task_ref: 'task_d', role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['record_check'] },
      { ref: 'fix_checkpoint', run_ref: run.ref, phase_ref: 'checkpoint', task_ref: 'task_d', role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['record_checkpoint'] },
      { ref: 'occ_review_two', run_ref: run.ref, phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [] },
    ],
    records: [], unknown_records: [{ ref: 'legacy_unknown', run_ref: run.ref, source_seq: 99, code: 'unsupported_observation' }],
    edges: [
      { ref: 'trigger', run_ref: run.ref, type: 'chain_trigger', from_ref: 'review_one', to_ref: 'fix_one', resolution: 'recorded' },
      { ref: 'check', run_ref: run.ref, type: 'chain_check', from_ref: 'fix_one', to_ref: 'record_check', resolution: 'recorded' },
      { ref: 'checkpoint', run_ref: run.ref, type: 'chain_checkpoint', from_ref: 'fix_one', to_ref: 'record_checkpoint', resolution: 'recorded' },
      { ref: 'predecessor', run_ref: run.ref, type: 'chain_predecessor', from_ref: 'fix_one', to_ref: 'review_two', resolution: 'recorded' },
    ],
    snapshot_ref: 'chain_snapshot', next_cursor: null,
    inventory: { phase_count: 0, occurrence_count: 6, observation_count: 0, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 1 },
  }
}

test.beforeAll(async () => {
  vite = await createViteServer({ server: { middlewareMode: true }, appType: 'spa' })
  server = createServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname === `/api/monitor/v1/runs/${run.ref}/snapshot`) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot())); return }
    if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: [] })); return }
    vite.middlewares(request, response, () => { response.statusCode = 404; response.end() })
  })
  await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve))
})
test.afterAll(async () => { await new Promise<void>(resolve => server.close(() => resolve())); await vite.close() })

test('shows a recorded chain overview, inert details, and preserves deliberate navigation on status refresh', async ({ page }) => {
  await page.clock.install()
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  const graph = page.getByLabel('Workflow graph')
  await expect(page.locator('.react-flow__node[data-id="review_one"]')).toContainText('Review 1')
  await expect(page.locator('.react-flow__node[data-id="fix_one"]')).toContainText('Fixing agent')
  await expect(page.locator('.react-flow__node[data-id="review_two"]')).toContainText('Review 2')
  await expect(page.locator('.react-flow__node[data-id="fix_check"]')).toBeVisible()
  await expect(page.getByTestId('rf__edge-trigger').getByText('Recorded trigger')).toBeVisible()
  await expect(page.getByTestId('rf__edge-check').getByText('Fixer check')).toBeVisible()
  await expect(page.getByTestId('rf__edge-checkpoint').getByText('Fixer checkpoint')).toBeVisible()
  const panel = await graph.boundingBox()
  if (!panel) throw new Error('Graph panel is missing')
  for (const id of ['task_a', 'task_d', 'review_one', 'fix_one', 'review_two']) {
    const box = await page.locator(`.react-flow__node[data-id="${id}"]`).boundingBox()
    expect(box, `${id} is not in the initial overview`).not.toBeNull()
    expect(box!.x).toBeGreaterThanOrEqual(panel.x)
    expect(box!.x + box!.width).toBeLessThanOrEqual(panel.x + panel.width)
    expect(box!.y).toBeGreaterThanOrEqual(panel.y)
    expect(box!.y + box!.height).toBeLessThanOrEqual(panel.y + panel.height)
  }
  await page.locator('.react-flow__node[data-id="review_one"]').click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('outcome rejected')
  await expect(details).toContainText('src/example.ts:7 - synthetic rejection')
  await expect(details.locator('img')).toHaveCount(0)
  await page.getByTitle('Zoom In').click()
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', /scale\(1\.2\)/)
  const beforeViewport = await page.locator('.react-flow__viewport').getAttribute('style')
  await page.clock.fastForward(60_000)
  await expect(page.locator('.react-flow__node[data-id="review_two"]')).toContainText('rejected — 1 finding')
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', beforeViewport ?? '')
  await expect(page.locator('.react-flow__node[data-id="review_one"]')).toHaveClass(/selected/)
  await page.getByText('Loaded history and technical references').click()
  await expect(page.getByText(/unsupported unsupported_observation; legacy_unknown/)).toBeVisible()
})
