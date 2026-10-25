import { test, expect } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'
import { resolve } from 'node:path'
import { graphFor, type GraphSnapshot } from '../src/graph'

let fixture: ChildProcess
let fixtureOutput = ''
let projectRef = ''
let mainQualifier = ''
const api = (suffix = '') => `http://127.0.0.1:4174/api/monitor/v1/projects/${encodeURIComponent(projectRef)}/runs${suffix}`
const runPage = (id: string) => `/projects/${encodeURIComponent(projectRef)}/runs/id-${encodeURIComponent(`${mainQualifier}-${id}`)}`

async function ready() {
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch('http://127.0.0.1:4174/api/monitor/v1/projects', { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
      if (response.ok) { const project = (await response.json()).projects[0]; projectRef = project?.ref ?? ''; mainQualifier = project?.recordings.find((item: { label: string }) => item.label === 'main')?.ref.split('_')[1] ?? ''; if (projectRef && (await fetch(api(), { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })).ok) return }
    } catch { /* fixture is still starting */ }
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  throw new Error(`Production execution fixture did not start: ${fixtureOutput}`)
}

test.beforeAll(async () => {
  const web = resolve(import.meta.dirname, '..')
  fixture = spawn(resolve(web, '../.venv/bin/python'), ['-B', 'tests/execution_fixture.py'], {
    cwd: web,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', PYTHONPATH: `${resolve(web, '../..')}/runtime:${resolve(web, '../..')}/runtime/tests` },
  })
  fixture.stdout?.on('data', chunk => { fixtureOutput += chunk })
  fixture.stderr?.on('data', chunk => { fixtureOutput += chunk })
  await ready()
})
test.afterAll(async () => {
  if (fixture.exitCode !== null) return
  const exited = new Promise<void>(resolve => fixture.once('exit', () => resolve()))
  fixture.kill('SIGTERM')
  await exited
})

test('inspects every merged input and correction fact with readable action endpoints', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto(runPage('merged-edge'))
  await expect(page.locator('.react-flow__node')).toHaveCount(3)
  await expect(page.locator('.react-flow__node').last()).toBeInViewport()
  const edge = page.locator('.react-flow__edge-interaction')
  await expect(edge).toHaveCount(2)
  const point = await edge.last().evaluate(element => {
    const path = element as SVGPathElement
    const point = path.getPointAtLength(path.getTotalLength() / 2)
    const screen = new DOMPoint(point.x, point.y).matrixTransform(path.getScreenCTM()!)
    return { x: screen.x, y: screen.y }
  })
  await page.mouse.click(point.x, point.y)
  const details = page.getByLabel('Selected execution details')
  await expect(details.getByRole('heading', { name: 'Recorded relationships', exact: true })).toBeVisible()
  await expect(details.locator(':scope > p').first()).toHaveText('Task 1 — Worker — Prepare result → Task 1 — Worker — Correction 1 — Prepare result')
  await expect(details.getByText('Recorded input', { exact: true })).toBeVisible()
  await expect(details.getByText('Recorded correction', { exact: true })).toBeVisible()
  await expect(details).not.toContainText('producerRef')
  await expect(details).not.toContainText('consumerRef')
  await expect(details).not.toContainText('predecessorRef')
  await expect(details).not.toContainText('correctionRef')
})

test('producer readback reconciles ordinal-two dispatch and qualifies observed lifecycle', async ({ page }) => {
  for (const [stage, expected] of [['dispatched', 'unknown'], ['started', 'running'], ['waiting', 'waiting'], ['returned', 'returned — changes requested'], ['conflict', 'unknown']] as const) {
    const response = await fetch(api(), { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
    const { runs } = await response.json()
    const run = runs.find((item: { display_id: string }) => item.display_id === `${mainQualifier}-review-${stage}`)
    const snapshotResponse = await fetch(api(`/${run.ref}/snapshot`), { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
    const input: GraphSnapshot = await snapshotResponse.json()
    const execution = input.chain!.find(item => item.review_ordinal === 2)!
    const activity = input.activities!.find(item => item.invocation_id === execution.execution_id)!
    expect(activity.ref).not.toBe(activity.invocation_id)
    const graph = graphFor(input, [], [])
    expect(graph.nodes.filter(node => node.id === execution.ref)).toHaveLength(1)
    expect(graph.nodes.some(node => node.id === activity.ref)).toBe(false)
    expect(graph.nodes.find(node => node.id === execution.ref)?.data.status).toContain(expected)
    await page.goto(runPage(`review-${stage}`))
    const node = page.locator('.react-flow__node').filter({ hasText: 'Review 2' })
    await expect(node).toHaveCount(1)
    await node.click()
    await expect(page.getByLabel('Selected execution details')).toContainText(`Execution: ${expected}`)
    await page.getByText('Loaded history', { exact: true }).click()
    for (const raw of ['recorded_running', 'outstanding_input', 'incomplete_history', 'conflicting_terminal_evidence']) await expect(page.locator('main')).not.toContainText(raw)
  }
  await page.goto(runPage('before-agent'))
  await expect(page.locator('.react-flow__node').filter({ hasText: 'Final review' })).toContainText('Not started; run stopped')
})

test('unobserved ordinal-two reviewer retains exact call metrics in Details', async ({ page }, testInfo) => {
  const headers = { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' }
  const { runs } = await (await fetch(api(), { headers })).json()
  const run = runs.find((item: { display_id: string }) => item.display_id === `${mainQualifier}-review-dispatched`)
  const input = await (await fetch(api(`/${run.ref}/snapshot`), { headers })).json()
  const execution = input.chain.find((item: { review_ordinal: number }) => item.review_ordinal === 2)
  const activity = input.activities.find((item: { invocation_id: string }) => item.invocation_id === execution.execution_id)
  expect(activity.occurrence_ref).toBeNull()
  expect(activity.metrics.total_tokens.value).toBe(12)
  expect(activity.ref).not.toBe(activity.invocation_id)
  await page.goto(runPage('review-dispatched'))
  const reviewer = page.locator('.react-flow__node').filter({ hasText: 'Review 2' })
  await expect(reviewer).toHaveCount(1)
  await expect(page.locator('.react-flow__node')).toHaveCount(5)
  await reviewer.click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Role: Reviewer; outcome: Recorded.')
  await expect(details).toContainText('Total tokens: 12')
  await expect(details).toContainText('Total tokens: known subtotal 12; complete total 12')
  await expect(details).not.toContainText('private-review-two')
  await expect(details).not.toContainText('Metrics unavailable: no recorded metric evidence')
  await details.getByRole('heading', { name: 'This call', exact: true }).scrollIntoViewIfNeeded()
  await page.screenshot({ path: testInfo.outputPath('production-unobserved-review-metrics.png'), fullPage: true })
})

test('ordinary task correction reports its recorded metric role', async ({ page }, testInfo) => {
  await page.goto(runPage('metrics-composed'))
  await page.locator('.react-flow__node').filter({ hasText: 'Worker — Correction 1' }).first().click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Role: Corrective worker; outcome: Recorded.')
  await expect(details).toContainText('Total tokens: 12')
  await expect(details).toContainText('Total tokens: known subtotal 24; complete total Unavailable')
  await expect(details).not.toContainText('corrective_worker')
  await details.getByRole('heading', { name: 'This call', exact: true }).scrollIntoViewIfNeeded()
  await page.screenshot({ path: testInfo.outputPath('production-ordinary-correction-metrics.png'), fullPage: true })
})

test('production computed lifecycle colors and declared recorded mixed connectors', async ({ page }, testInfo) => {
  const colors = [['review-started', 'Review 2', 'rgb(220, 236, 255)'], ['review-waiting', 'Review 2', 'rgb(255, 240, 194)'], ['review-returned', 'Review 2', 'rgb(220, 245, 228)'], ['review-conflict', 'Review 2', 'rgb(238, 242, 246)'], ['before-agent', 'Final review', 'rgb(229, 231, 235)'], ['waiting', 'Task 1', 'rgb(255, 240, 194)']] as const
  for (const [run, title, color] of colors) {
    await page.goto(runPage(run))
    const node = page.locator('.react-flow__node').filter({ hasText: title })
    await expect(node).toHaveCSS('background-color', color)
    expect((await node.getAttribute('class'))?.split(' ').filter(value => ['pending', 'running', 'success', 'failed', 'waiting', 'neutral'].includes(value))).toHaveLength(1)
  }
  await page.goto(runPage('relation-styles'))
  for (const [kind, stroke, dash] of [['declared', 'rgb(95, 75, 182)', '6px, 4px'], ['recorded', 'rgb(23, 105, 170)', 'none'], ['mixed', 'rgb(40, 117, 107)', '8px, 3px, 2px, 3px']] as const) {
    const path = page.locator(`.${kind}-edge .react-flow__edge-path`).first()
    await expect(path).toHaveCSS('stroke', stroke)
    await expect(path).toHaveCSS('stroke-dasharray', dash)
  }
  const mixed = page.locator('.mixed-edge .react-flow__edge-interaction')
  const point = await mixed.evaluate(element => { const path = element as SVGPathElement; const p = path.getPointAtLength(path.getTotalLength() / 2); const s = new DOMPoint(p.x, p.y).matrixTransform(path.getScreenCTM()!); return { x: s.x, y: s.y } })
  await page.mouse.click(point.x, point.y)
  await expect(page.getByLabel('Selected execution details')).toContainText('both a declared dependency and a recorded execution relationship')
  await expect(page.getByLabel('Selected execution details')).toContainText('Declared prerequisite')
  await expect(page.getByLabel('Selected execution details')).toContainText('Recorded input')
  await page.screenshot({ path: testInfo.outputPath('production-mixed-relations.png'), fullPage: true })
})

test('compaction inclusion uncertainty is honest and never changes totals', async ({ page }) => {
  for (const [run, text] of [['success', 'This summary is already included in This call and is not added again.'], ['metrics-excluded', 'This summary is not included in the recorded call deltas. Do not infer a combined total.'], ['metrics-unverified', 'Inclusion in the recorded call deltas is unverified. Do not infer a combined total.']] as const) {
    // The artifact writer requires a boolean; exercise the nullable public DTO
    // branch by changing only inclusion on an otherwise real HTTP readback.
    if (run === 'metrics-unverified') await page.route('**/snapshot', async route => {
      const response = await fetch(route.request().url(), { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
      expect(response.ok).toBe(true)
      const body = await response.json()
      for (const activity of body.activities ?? []) if (activity.metrics?.summary_overhead) activity.metrics.summary_overhead.included_in_sdk_deltas = null
      await route.fulfill({ json: body })
    })
    await page.goto(runPage(run === 'metrics-unverified' ? 'success' : run))
    await page.locator('.react-flow__node').first().click()
    const details = page.getByLabel('Selected execution details')
    await expect(details).toContainText(text)
    await expect(details).toContainText('Total tokens: 12')
    await expect(details).toContainText('Total tokens: known subtotal 12; complete total 12')
    await expect(details).toContainText('Total tokens: 3')
    await expect(details).not.toContainText('Total tokens: 15')
  }
})

test('renders scoped ordinary metrics from fixture JSONL through production HTTP', async ({ page }, testInfo) => {
  await page.goto(runPage('success'))
  const worker = page.locator('.react-flow__node').first()
  await expect(worker).toBeVisible()
  await worker.click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Task 1')
  await expect(details).toContainText('Full retained work text: <img src=x onerror=alert(1)> Recorded workflow explanation')
  await expect(details).toContainText('opaque-invocation-identity')
  await expect(details.locator('img')).toHaveCount(0)
  await expect(details).not.toContainText('Task ID:')
  for (const value of ['This call', 'Input tokens: 5', 'Output tokens: 7', 'Total tokens: 12', 'Cost: 0.25', 'Before session total', 'After session total', 'Available context: -30', 'Compaction enabled: false', 'Compaction enabled: true', 'This summary is already included in This call and is not added again.', 'Task total', 'Overall run — workers and corrective workers', 'Overall run — reviewers (not task spend)']) await expect(details).toContainText(value)
  for (const forbidden of ['invocation_interval', 'success-worker', 'session-one', 'branch-one', 'epoch-one', 'fixture-selection', 'compact-one', 'already_included_do_not_add', 'cacheWrite1h', 'sdk_cumulative_counters.input', '[fixture]', 'estimated_usd', 'provenance']) await expect(details).not.toContainText(forbidden)
  await page.screenshot({ path: testInfo.outputPath('production-metrics-overview.png'), fullPage: true })
  await details.getByRole('heading', { name: 'This call', exact: true }).scrollIntoViewIfNeeded()
  await page.screenshot({ path: testInfo.outputPath('production-metrics-this-call.png'), fullPage: true })
  await details.getByText('Acceptance history').click()
  await expect(details).toContainText('Check 1: Failed; exit 1.')
  await page.screenshot({ path: testInfo.outputPath('production-metrics-details-expanded.png'), fullPage: true })

  for (const [run, opening] of [['metrics-reused', 'Session reused from an earlier task'], ['metrics-continued', 'Session continued for this task'], ['metrics-unknown', 'Opening not recorded']] as const) {
    await page.goto(runPage(run))
    await page.locator('.react-flow__node').first().click()
    await expect(page.getByLabel('Selected execution details')).toContainText(`Selected opening: ${opening}. Confirmed opening: ${opening}.`)
  }
  await page.goto(runPage('metrics-composed'))
  await page.locator('.react-flow__node.actual-call').first().click()
  await expect(details).toContainText('Task total')
  await expect(details).toContainText('Total tokens: known subtotal 24; complete total Unavailable')
  await expect(details).toContainText('Overall run — workers and corrective workers')
  await expect(details).toContainText('Total tokens: known subtotal 36; complete total Unavailable')
  await expect(details).toContainText('Overall run — reviewers (not task spend)')
  await expect(details).toContainText('Recorded metric evidence is incomplete or unavailable.')
  await expect(details).not.toContainText('/PRIVATE/error')
  await page.locator('.react-flow__node').filter({ hasText: 'Final review' }).click()
  await expect(details).toContainText('Role: Reviewer; outcome: Recorded.')
  await expect(details).toContainText('Total tokens: 12')
  await page.goto(runPage('engine-correction'))
  await page.locator('.react-flow__node').filter({ hasText: 'Fix 1' }).click()
  await expect(details).toContainText('Role: Corrective worker; outcome: Recorded.')
  await expect(details).toContainText('Total tokens: 12')
  await expect(details).toContainText('Total tokens: known subtotal 24; complete total 24')
  await expect(details).toContainText('2 recorded calls; 2 dispatched calls; 1 task membership.')
  await page.goto(runPage('metrics-partial'))
  await page.locator('.react-flow__node').first().click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Partial recorded coverage. Some recorded intervals or dispatches are incomplete.')
  await expect(page.getByLabel('Selected execution details')).toContainText('Output tokens: Unavailable from the recorded evidence')
})
