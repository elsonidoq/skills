import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { createServer as createViteServer, type ViteDevServer } from 'vite'

let server: Server
let vite: ViteDevServer
const run = { ref: 'run', display_id: 'rendered-chain', label: 'Rendered activity chain', completeness: 'recorded', started_at: 1 }
const snapshot = () => ({
  runs: [run], phases: [], tasks: [{ ref: 'task', run_ref: 'run', task_id: 'T005', label: 'Task', work_description: 'Measured activity rendering', prerequisite_refs: [] }], records: [], review_definitions: [], unknown_records: [], inventory: { phase_count: 0, occurrence_count: 1, observation_count: 0, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 0 }, snapshot_ref: 'fixture', next_cursor: null,
  occurrences: [{ ref: 'stop', run_ref: 'run', phase_ref: 'terminal', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'fix' }],
  activities: [
    { ref: 'worker', run_ref: 'run', invocation_id: 'worker', occurrence_ref: 'worker-occ', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: ['worker'], support_ref: null, stopped_by_ref: null, record_refs: [] },
    { ref: 'branch', run_ref: 'run', invocation_id: 'branch', occurrence_ref: 'branch-occ', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['worker'], correction_chain: ['branch'], support_ref: null, stopped_by_ref: null, record_refs: [] },
    { ref: 'fix', run_ref: 'run', invocation_id: 'fix', occurrence_ref: 'fix-occ', task_ref: 'task', role: 'fixing_worker', invocation_kind: 'corrective_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: ['worker', 'branch'], correction_chain: ['worker', 'fix'], support_ref: null, stopped_by_ref: null, record_refs: [] }
  ],
  chain: [{ ref: 'review', run_ref: 'run', execution_id: 'review', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: 'fix', predecessor_ref: null, occurrence_refs: [], review_range: { base: null, head: null }, findings: ['src/activity.ts:1 - review finding'], commit_refs: {} }]
})

test.beforeAll(async () => {
  vite = await createViteServer({ server: { middlewareMode: true }, appType: 'spa', plugins: [{
    name: 'hold-layout-result-for-stale-run-test', enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/layout.ts')) return
      const seam = '  const layout = await elk.layout(elkInput)'
      if (!code.includes(seam)) throw new Error('Layout test seam not found')
      return code.replace(seam, `${seam}\n  await (window as any).__holdLayoutResult?.(nodes)`)
    }
  }] })
  server = createServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/projects') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ projects: [{ ref: 'project', label: 'Fixture', recordings: [] }] })); return }
    if (url.pathname.endsWith('/runs')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname.endsWith('/runs/run/snapshot')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot())); return }
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
  expect(geometry.every(item => item.width >= 208 && item.height >= 90)).toBeTruthy()
  await expect.poll(() => nodes.evaluateAll(items => items.every(item => { const bounds = item.getBoundingClientRect(); return [...item.querySelectorAll('strong, small')].every(text => { const rect = text.getBoundingClientRect(); return rect.left >= bounds.left - 1 && rect.right <= bounds.right + 1 && rect.bottom <= bounds.bottom + 1 }) }))).toBeTruthy()
  const edgePaths = page.locator('.react-flow__edge-path')
  expect(await edgePaths.evaluateAll(paths => paths.every(path => (path as SVGPathElement).getTotalLength() > 0))).toBeTruthy()
  await page.locator('.react-flow__node[data-id="review"]').click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Execution: returned — changes requested')
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
  const node = page.locator('.react-flow__node[data-id="worker"]')
  const nodeBox = (await node.boundingBox())!
  const edgeBefore = await edgePaths.first().getAttribute('d')
  await page.mouse.move(nodeBox.x + nodeBox.width / 2, nodeBox.y + nodeBox.height / 2)
  await page.mouse.down(); await page.mouse.move(nodeBox.x + nodeBox.width / 2 + 40, nodeBox.y + nodeBox.height / 2 + 30, { steps: 5 }); await page.mouse.up()
  await expect(edgePaths.first()).not.toHaveAttribute('d', edgeBefore!)
  const moved = await page.locator('.react-flow__viewport').getAttribute('style')
  await page.locator('.react-flow__controls-zoomin').click()
  await expect(page.locator('.react-flow__viewport')).not.toHaveAttribute('style', moved!)
  await page.locator('.react-flow__controls-interactive').click()
  await expect(page.locator('.react-flow__controls-interactive')).toHaveAttribute('title', /interactivity/i)
  await page.locator('.react-flow__controls-interactive').click()
  await page.locator('.react-flow__controls-fitview').click()
})

test('rejects a completed old-run layout after switching runs', async ({ page }) => {
  const nextRun = { ...run, ref: 'next-run', display_id: 'next-chain', label: 'Next activity chain' }
  const oldToNew: Record<string, string> = Object.fromEntries(['run', 'task', 'worker', 'worker-occ', 'branch', 'branch-occ', 'fix', 'fix-occ', 'stop', 'review'].map(id => [id, `next-${id}`]))
  const nextSnapshot = JSON.parse(JSON.stringify(snapshot(), (_key, value) => typeof value === 'string' ? oldToNew[value] ?? value : value))
  nextSnapshot.runs = [nextRun]
  nextSnapshot.snapshot_ref = 'next-fixture'
  await page.route('**/api/monitor/v1/projects/project/runs', route => route.fulfill({ json: { runs: [run, nextRun] } }))
  await page.route('**/runs/next-run/snapshot', route => route.fulfill({ json: nextSnapshot }))
  await page.addInitScript(() => {
    const state = window as any
    state.__oldLayoutHeld = 0
    state.__oldLayoutReleased = 0
    const releases: Array<() => void> = []
    state.__holdLayoutResult = async (nodes: Array<{ id: string }>) => {
      if (!nodes.some(node => node.id === 'worker')) return
      state.__oldLayoutHeld++
      await new Promise<void>(resolve => releases.push(resolve))
      state.__oldLayoutReleased++
    }
    state.__releaseOldLayouts = () => releases.splice(0).forEach(resolve => resolve())
  })
  await page.goto('/projects/project/runs/id-rendered-chain')
  await expect.poll(() => page.evaluate(() => (window as any).__oldLayoutHeld)).toBeGreaterThan(0)
  await page.locator('.run-list button').filter({ hasText: 'Next activity chain' }).click()
  const nodes = page.locator('.react-flow__node[data-id]')
  await expect(nodes).toHaveCount(6)
  await expect(page.locator('.react-flow__node[data-id="next-worker"]')).toBeVisible()
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(5)
  await expect(page.locator('.react-flow__viewport')).not.toHaveAttribute('style', 'transform: translate(0px, 0px) scale(1);')
  // Wait for the new run's measurements and layout to settle before releasing the old result.
  await expect.poll(() => nodes.evaluateAll(items => items.every(item => getComputedStyle(item).visibility === 'visible'))).toBe(true)
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))))
  const before = await nodes.evaluateAll(items => items.map(item => ({ id: (item as HTMLElement).dataset.id, transform: (item as HTMLElement).style.transform, width: (item as HTMLElement).style.width, height: (item as HTMLElement).style.height })))
  const edges = await page.locator('.react-flow__edge-path').evaluateAll(items => items.map(item => item.getAttribute('d')))
  const viewport = await page.locator('.react-flow__viewport').getAttribute('style')
  const held = await page.evaluate(() => (window as any).__oldLayoutHeld as number)
  await page.evaluate(() => (window as any).__releaseOldLayouts())
  await expect.poll(() => page.evaluate(() => (window as any).__oldLayoutReleased)).toBe(held)
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))))
  await expect(page.getByLabel('Selected run')).toContainText('Next activity chain')
  expect(await nodes.evaluateAll(items => items.map(item => ({ id: (item as HTMLElement).dataset.id, transform: (item as HTMLElement).style.transform, width: (item as HTMLElement).style.width, height: (item as HTMLElement).style.height })))).toEqual(before)
  expect(await page.locator('.react-flow__edge-path').evaluateAll(items => items.map(item => item.getAttribute('d')))).toEqual(edges)
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', viewport!)
})

test('content size and topology changes are measured on refresh', async ({ page }) => {
  await page.clock.install()
  let changed = false
  await page.route('**/runs/run/snapshot', route => {
    const data = snapshot()
    if (changed) {
      data.tasks[0].work_description = 'A longer retained description that wraps across several lines and needs more measured space for the activity node and its status.'
      data.activities.push({ ...data.activities[1], ref: 'extra', invocation_id: 'extra', occurrence_ref: 'extra-occ', input_refs: ['branch'], correction_chain: ['extra'] })
    }
    return route.fulfill({ json: data })
  })
  await page.goto('/')
  await expect(page.locator('.react-flow__node')).toHaveCount(6)
  const worker = page.locator('.react-flow__node[data-id="worker"]')
  const initialHeight = await worker.evaluate(element => (element as HTMLElement).offsetHeight)
  changed = true
  await page.clock.fastForward(60_001)
  await expect(page.locator('.react-flow__node')).toHaveCount(7)
  await expect(page.locator('.react-flow__node').filter({ hasText: 'longer retained description' }).first()).toBeVisible()
  await expect.poll(() => worker.evaluate(element => (element as HTMLElement).offsetHeight)).toBeGreaterThan(initialHeight)
  await expect(page.locator('.react-flow__edge-path')).toHaveCount(6)
})
