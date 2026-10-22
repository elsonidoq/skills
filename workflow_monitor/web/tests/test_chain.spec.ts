import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { createServer as createViteServer, type ViteDevServer } from 'vite'

let server: Server
let vite: ViteDevServer
const run = { ref: 'run', display_id: 'rendered-chain', label: 'Rendered activity chain', completeness: 'recorded', started_at: 1 }
const snapshot = () => ({
  runs: [run], phases: [], tasks: [{ ref: 'task', run_ref: 'run', task_id: 'T005', label: 'Task', summary: 'Measured activity rendering', prerequisite_refs: [] }], records: [], review_definitions: [], unknown_records: [], inventory: { phase_count: 0, occurrence_count: 1, observation_count: 0, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 0 }, snapshot_ref: 'fixture', next_cursor: null,
  occurrences: [{ ref: 'stop', run_ref: 'run', phase_ref: 'terminal', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'fix' }],
  activities: [
    { ref: 'worker', run_ref: 'run', invocation_id: 'worker', occurrence_ref: 'worker-occ', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: ['worker'], support_ref: null, stopped_by_ref: null, record_refs: [] },
    { ref: 'branch', run_ref: 'run', invocation_id: 'branch', occurrence_ref: 'branch-occ', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['worker'], correction_chain: ['branch'], support_ref: null, stopped_by_ref: null, record_refs: [] },
    { ref: 'fix', run_ref: 'run', invocation_id: 'fix', occurrence_ref: 'fix-occ', task_ref: 'task', role: 'fixing_worker', invocation_kind: 'corrective_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['worker', 'branch'], correction_chain: ['worker', 'fix'], support_ref: null, stopped_by_ref: null, record_refs: [] }
  ],
  chain: [{ ref: 'review', run_ref: 'run', execution_id: 'review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: 'fix', predecessor_ref: null, occurrence_refs: [], review_range: { base: null, head: null }, findings: ['src/activity.ts:1 - review finding'], commit_refs: {} }]
})

test.beforeAll(async () => {
  vite = await createViteServer({ server: { middlewareMode: true }, appType: 'spa' })
  server = createServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname === '/api/monitor/v1/runs/run/snapshot') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot())); return }
    if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: [] })); return }
    vite.middlewares(request, response, () => { response.statusCode = 404; response.end() })
  })
  await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve))
})
test.afterAll(async () => { await new Promise<void>(resolve => server.close(() => resolve())); await vite.close() })

test('renders a flat measured DOWN activity graph and preserves interaction state', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  const nodes = page.locator('.react-flow__node[data-id]')
  await expect(nodes).toHaveCount(6)
  await page.screenshot({ path: testInfo.outputPath('flat-activity-overview.png') })
  await expect(page.locator('.owner-group')).toHaveCount(0)
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(5)
  const geometry = await nodes.evaluateAll(items => items.map(item => ({ id: (item as HTMLElement).dataset.id, width: (item as HTMLElement).offsetWidth, height: (item as HTMLElement).offsetHeight })))
  expect(geometry.every(item => item.width > 0 && item.height > 0)).toBeTruthy()
  await page.locator('.react-flow__node[data-id="review"]').click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Outcome: returned — changes requested')
  const pane = page.locator('.react-flow__pane'); const box = await pane.boundingBox(); if (!box) throw new Error('Missing graph pane')
  const before = await page.locator('.react-flow__viewport').getAttribute('style')
  await page.mouse.move(box.x + 200, box.y + 200); await page.mouse.down(); await page.mouse.move(box.x + 260, box.y + 240)
  // Keep the T001 boundary: the controlled viewport changes while the pointer is held,
  // and already measured calls/connectors never disappear during the movement.
  await page.waitForTimeout(100)
  const whileHeld = await page.locator('.react-flow__viewport').getAttribute('style')
  expect(whileHeld).not.toBe(before)
  await expect(nodes).toHaveCount(6)
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(5)
  await expect(nodes.evaluateAll(items => items.every(item => { const style = getComputedStyle(item); const box = item.getBoundingClientRect(); return style.visibility === 'visible' && box.width > 0 && box.height > 0 }))).resolves.toBeTruthy()
  await page.mouse.up()
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', whileHeld ?? '')
  await expect(page.locator('.react-flow__node[data-id="review"]')).toHaveClass(/selected/)
})
