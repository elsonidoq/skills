import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'

let server: Server
let runTwoSnapshots = 0
let writes = 0

const runs = [{ ref: 'run_one', label: 'Old run', completeness: 'recorded', started_at: 1 }, { ref: 'run_two', label: 'Current run', completeness: 'recorded', started_at: 2 }]

function snapshot(run: string, changed = false) {
  const current = run === 'run_two'
  const phase = current ? 'phase_two' : 'phase_one'
  const occurrence = current ? 'occ_reviewer' : 'occ_worker'
  const record = current ? 'record_two' : 'record_one'
  const outcome = current && changed ? 'failed' : 'passed'
  return {
    runs,
    phases: [{ ref: phase, run_ref: run, label: current ? 'Review' : 'Worker' }], tasks: [],
    occurrences: [...(current ? [{ ref: 'preceding_worker', run_ref: run, phase_ref: phase, task_ref: null, role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [], first_seq: 0 }] : []), { ref: occurrence, run_ref: run, phase_ref: phase, task_ref: null, role: current ? 'reviewer' : 'worker', outcome, completeness: 'complete', record_refs: [record] }],
    records: [{ ref: record, run_ref: run, occurrence_ref: occurrence, kind: outcome, source_seq: 1, recorded_at: 1, exit_code: outcome === 'failed' ? 1 : 0, finding_count: null, review_base: null, review_head: null }],
    edges: [{ ref: `edge_${run}`, run_ref: run, type: 'phase_occurrence', from_ref: phase, to_ref: occurrence, resolution: 'recorded' }, { ref: `milestone_${run}`, run_ref: run, type: 'execution_milestone', from_ref: occurrence, to_ref: record, resolution: 'recorded' }],
    inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, hidden_count: 0 }
  }
}

test.beforeAll(async () => {
  server = createServer(async (request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (request.method !== 'GET') { writes++; response.statusCode = 405; response.end(); return }
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs })); return }
    const match = url.pathname.match(/^\/api\/monitor\/v1\/runs\/(run_(?:one|two))\/snapshot$/)
    if (match) {
      response.setHeader('content-type', 'application/json')
      if (match[1] === 'run_one') { setTimeout(() => response.end(JSON.stringify(snapshot('run_one'))), 350); return }
      runTwoSnapshots++
      response.end(JSON.stringify(snapshot('run_two', runTwoSnapshots > 1)))
      return
    }
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

test.afterAll(async () => {
  await new Promise<void>(resolve => server.close(() => resolve()))
  expect(writes).toBe(0)
})

test('keeps live navigation stable and ignores an old selected-run response', async ({ page }) => {
  await page.clock.install(); await page.goto('/')
  await expect(page.getByRole('button', { name: /Current run/ })).toBeVisible()
  await page.getByRole('button', { name: /Current run/ }).click()
  await expect(page.locator('.react-flow__node[data-id="occ_reviewer"]')).toBeVisible()
  await page.locator('.react-flow__node[data-id="occ_reviewer"]').click()
  await expect(page.getByLabel('Selected execution details').getByText(/reviewer; passed/)).toBeVisible()
  await page.locator('.react-flow__edge[data-id="sequence_preceding_worker_occ_reviewer"] .react-flow__edge-path').click({ force: true })
  await expect(page.getByLabel('Selected execution details').getByText(/Recorded relation:/)).toBeVisible()
  await page.getByTitle('Zoom In').click()
  await page.waitForTimeout(600)
  const pane = await page.locator('.react-flow__pane').boundingBox()
  if (!pane) throw new Error('Graph pane is missing')
  await page.mouse.move(pane.x + 25, pane.y + pane.height - 35)
  await page.mouse.down(); await page.mouse.move(pane.x + 65, pane.y + pane.height - 55, { steps: 5 }); await page.mouse.up()
  const viewport = await page.locator('.react-flow__viewport').getAttribute('style')
  const position = await page.locator('.react-flow__node[data-id="occ_reviewer"]').getAttribute('style')
  await page.clock.fastForward(60_000)
  await expect(page.locator('.react-flow__node[data-id="occ_reviewer"]')).toHaveClass(/failed/)
  await expect(page.getByLabel('Selected execution details').getByText(/Recorded relation:/)).toBeVisible()
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', viewport ?? '')
  await expect(page.locator('.react-flow__node[data-id="occ_reviewer"]')).toHaveAttribute('style', position ?? '')
  await page.locator('.react-flow__node[data-id="occ_reviewer"]').click()
  await page.clock.fastForward(60_000)
  await expect(page.locator('.react-flow__node[data-id="occ_reviewer"]')).toHaveClass(/selected/)
  await expect(page.getByLabel('Selected execution details')).toContainText('reviewer; failed')
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', viewport ?? '')
  await page.waitForTimeout(400)
  await expect(page.locator('.react-flow__node[data-id="occ_worker"]')).toHaveCount(0)
})
