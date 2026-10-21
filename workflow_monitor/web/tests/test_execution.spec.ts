import { test, expect } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'

let server: ChildProcess
let stderr = ''
test.beforeAll(async () => {
  server = spawn('../.venv/bin/python', ['-B', 'tests/execution_fixture.py'], { env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }, stdio: ['ignore', 'ignore', 'pipe'] })
  server.stderr?.on('data', chunk => { stderr += chunk.toString() })
  for (let attempt = 0; attempt < 100; attempt++) {
    if (server.exitCode !== null) throw new Error(`Offline recording fixture failed: ${stderr}`)
    try { const response = await fetch('http://127.0.0.1:4174/'); if (response.ok) return } catch { /* Server is starting. */ }
    await new Promise(resolve => setTimeout(resolve, 50))
  }
  throw new Error(`Offline recording fixture did not start: ${stderr}`)
})
test.afterAll(async () => {
  if (server.exitCode === null) { server.kill('SIGTERM'); await new Promise<void>(resolve => server.once('exit', () => resolve())) }
})
test('production HTTP compacts recorded executions, exposes stopping checks and visible details with honest colors', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  const snapshots: any[] = await page.evaluate(async () => {
    const headers = { 'X-Workflow-Monitor': '1' }
    const runs = (await (await fetch('/api/monitor/v1/runs', { headers })).json()).runs
    return Promise.all(runs.map(async (run: { ref: string }) => (await fetch(`/api/monitor/v1/runs/${run.ref}/snapshot`, { headers })).json()))
  })
  const select = async (predicate: (snapshot: any) => boolean) => {
    const index = snapshots.findIndex(predicate)
    expect(index).toBeGreaterThanOrEqual(0)
    await page.getByRole('button', { name: /Recorded run/ }).nth(index).click()
    return snapshots[index]
  }
  const stopped = await select(snapshot => snapshot.occurrences.some((item: any) => item.phase === 'check' && item.stopping))
  const worker = stopped.occurrences.find((item: any) => item.role === 'worker')
  const check = stopped.occurrences.find((item: any) => item.phase === 'check')
  expect(check.support_ref).toBe(worker.ref)
  await expect(page.locator('.react-flow__node')).toHaveCount(6)
  await expect(page.locator('.planned-node')).toHaveCount(3)
  await expect(page.locator('.planned-review-node')).toHaveCount(1)
  const workerNode = page.locator(`.react-flow__node[data-id="${worker.ref}"]`)
  const checkNode = page.locator(`.react-flow__node[data-id="${check.ref}"]`)
  await expect(workerNode).toContainText('Implement T001')
  await expect(workerNode).toHaveClass(/success/)
  await expect(workerNode).toContainText('returned — acceptance not established')
  await expect(checkNode).toContainText('Check T001')
  await expect(checkNode).toHaveClass(/failed/)
  await expect(checkNode).toHaveCSS('background-color', 'rgb(255, 229, 229)')
  await expect(page.locator('.react-flow__edge')).toHaveCount(4)
  await expect(page.locator('.react-flow__edge.dependency-edge')).toHaveCount(1)
  await expect(page.locator('.react-flow__edge.attachment-edge')).toHaveCount(2)
  await expect(page.getByTestId(`rf__edge-stop_${check.ref}`)).toHaveAttribute('data-id', `stop_${check.ref}`)
  await workerNode.click()
  await expect(workerNode).toHaveClass(/selected/)
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Check T001: failed')
  await expect(details).toContainText('exit 1')
  const box = await details.boundingBox()
  expect(box && box.y + Math.min(box.height, 100)).toBeLessThan(1000)
  await checkNode.click()
  await expect(details).toContainText('check 1; exit 1')
  await select(snapshot => snapshot.occurrences.some((item: any) => item.phase === 'prepare' && item.stopping))
  await expect(page.locator('.react-flow__node')).toHaveCount(5)
  await expect(page.locator('.execution-node')).toContainText('Prepare T001')
  await expect(page.locator('.react-flow__edge')).toHaveCount(2)
  await select(snapshot => snapshot.occurrences.some((item: any) => item.parent_ref && item.record_refs.length === 1) && snapshot.records.some((item: any) => item.kind === 'question_requested'))
  await expect(page.locator('.react-flow__node')).toHaveCount(5)
  await expect(page.locator('.execution-node')).toHaveClass(/waiting/); await expect(page.locator('.execution-node')).toContainText('waiting — recorded question')
  await expect(page.locator('.execution-node')).toHaveCSS('background-color', 'rgb(255, 240, 194)')
  await select(snapshot => snapshot.occurrences.some((item: any) => item.role === 'reviewer'))
  await expect(page.locator('.react-flow__node')).toHaveCount(6)
  const review = page.locator('.react-flow__node').filter({ hasText: /^Review/ })
  await expect(review).not.toContainText('T001')
  await expect(review).toHaveClass(/success/)
  await expect(review).toHaveCSS('background-color', 'rgb(220, 245, 228)')
  await page.locator('.react-flow__node').filter({ hasText: /^Implement/ }).click()
  await expect(details).toContainText('Checkpoint T001: passed')
  await expect(details).toContainText('no change true; baseline ')
  await expect(details).toContainText('Check T001: failed')
  await expect(details).toContainText('exit 1')
  await expect(page.locator('.react-flow__node.failed')).toHaveCount(0)
  await review.click()
  await expect(details).toContainText('approved true; findings 0')
  await expect(details).toContainText('range ')
  expect(stderr).not.toContain('PRIVATE-SENTINEL')
})

test('a question answered beyond the history page boundary does not falsely mark its worker waiting', async ({ page }) => {
  await page.goto('/')
  const views: any[] = await page.evaluate(async () => {
    const headers = { 'X-Workflow-Monitor': '1' }
    const runs = (await (await fetch('/api/monitor/v1/runs', { headers })).json()).runs
    return Promise.all(runs.map(async (run: { ref: string }) => (await fetch(`/api/monitor/v1/runs/${run.ref}/snapshot`, { headers })).json()))
  })
  const index = views.findIndex(view => view.next_cursor && view.occurrences.some((item: any) => item.parent_ref && item.record_refs.length === 3))
  expect(index).toBeGreaterThanOrEqual(0)
  const view = views[index]
  const question = view.occurrences.find((item: any) => item.parent_ref && item.record_refs.length === 3)
  expect(view.records).toHaveLength(50)
  expect(view.records[49].kind).toBe('question_requested')
  expect(view.records.filter((item: any) => question.record_refs.includes(item.ref))).toHaveLength(1)
  await page.getByRole('button', { name: /Recorded run/ }).nth(index).click()
  const worker = page.locator(`.react-flow__node[data-id="${question.parent_ref}"]`)
  await expect(page.locator('.react-flow__node')).toHaveCount(5)
  await expect(worker).toHaveClass(/success/)
  await expect(worker).not.toContainText('waiting')
  await expect(page.getByLabel('Collapsed history badges')).toContainText('0 waiting;')
  await page.getByRole('button', { name: 'Load more history', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Load more history', exact: true })).toHaveCount(0)
  await expect(worker).toHaveClass(/success/)
  await expect(worker).toContainText('returned — acceptance not established')
  await expect(page.getByLabel('Collapsed history badges')).toContainText('0 waiting;')
  await worker.click()
  await expect(page.getByLabel('Selected execution details')).toContainText('answer_sent')
})
