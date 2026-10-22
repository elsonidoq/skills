import { test, expect } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'
import { resolve } from 'node:path'

let fixture: ChildProcess
let fixtureOutput = ''

async function ready() {
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch('http://127.0.0.1:4174/api/monitor/v1/runs', { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
      if (response.ok) return
    } catch { /* fixture is still starting */ }
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  throw new Error(`Production execution fixture did not start: ${fixtureOutput}`)
}

test.beforeAll(async () => {
  const web = process.cwd()
  fixture = spawn(resolve(web, '../.venv/bin/python'), ['-B', 'tests/execution_fixture.py'], {
    cwd: web,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', PYTHONPATH: `${resolve(web, '../..')}/runtime:${resolve(web, '../..')}/runtime/tests` },
  })
  fixture.stdout?.on('data', chunk => { fixtureOutput += chunk })
  fixture.stderr?.on('data', chunk => { fixtureOutput += chunk })
  await ready()
})
test.afterAll(async () => {
  fixture.kill('SIGTERM')
  await new Promise<void>(resolve => fixture.once('exit', () => resolve()))
})

test('renders selected actual invocation metrics from the fixture JSONL through production HTTP', async ({ page }) => {
  await page.goto('/runs/id-success')
  const worker = page.locator('.react-flow__node').first()
  await expect(worker).toBeVisible()
  await worker.click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Execution outcome: returned — acceptance not established.')
  await expect(details.locator('img')).toHaveCount(0)
  await expect(details).toContainText('Availability: complete; coverage reasons: none recorded.')
  await expect(details).toContainText('invocation_interval; invocation success-worker; session session-one; branch branch-one; epoch epoch-one')
  await expect(details).toContainText('Selected opening: fresh; reason: fixture-selection. Confirmed opening: fresh; actual identity: session-one.')
  for (const value of ['input tokens: 5 [fixture]', 'output tokens: 7 [fixture]', 'cache-read tokens: 0 [fixture]', 'cache-write tokens: 0 [fixture]', 'total tokens: 12 [fixture]', 'estimated USD: 0.25 [fixture]', 'Invocation compactions: 1; references: compact-one', 'Before session cumulative (known)', 'After session cumulative (known)', 'effective headroom: -30', 'compaction enabled: false', 'compaction enabled: true', 'already_included_do_not_add', 'cacheWrite1h: 0', 'reasoning: 1', 'cost total: 0']) await expect(details).toContainText(value)
  await expect(details).toContainText('Selection intent is not a confirmed opening. Invocation usage is not task-wide dispatch totals or reviewer/session spend.')

  for (const [run, mode] of [['metrics-reused', 'reused_from_earlier_task'], ['metrics-continued', 'continued_same_task'], ['metrics-unknown', 'unknown']] as const) {
    await page.goto(`/runs/id-${run}`)
    await page.locator('.react-flow__node').click()
    await expect(page.getByLabel('Selected execution details')).toContainText(`Selected opening: ${mode}; reason: fixture-selection. Confirmed opening: ${mode}; actual identity: session-one.`)
  }
  await page.goto('/runs/id-metrics-composed')
  await page.locator('.react-flow__node').filter({ hasText: '(correction)' }).first().click()
  await expect(details).toContainText('Same-task dispatched calls')
  await expect(details).toContainText('total tokens: known subtotal 24; full total unavailable')
  await expect(details).toContainText('Run worker/fixer usage')
  await expect(details).toContainText('total tokens: known subtotal 36; full total unavailable')
  await expect(details).toContainText('Run reviewer usage (not task spend)')
  await expect(details).toContainText('Outcome: failed; path: .coherence/metrics/run-')
  await expect(details).not.toContainText('/PRIVATE/error')
  await page.locator('.react-flow__node').filter({ hasText: 'Review 1' }).click()
  await expect(details).toContainText('invocation_interval; invocation reviewer; session session-one')
  await expect(details).toContainText('Invocation role: reviewer')
  await expect(details).toContainText('total tokens: 12 [fixture]')
  await page.goto('/runs/id-engine-correction')
  await page.locator('.react-flow__node').filter({ hasText: '(correction)' }).click()
  await expect(details).toContainText('Invocation role: fixing_worker')
  await expect(details).toContainText('total tokens: 12 [fixture]')
  await expect(details).toContainText('total tokens: known subtotal 24; full total 24')
  await expect(details).toContainText('Recorded intervals: 2; dispatched calls: 2; distinct task memberships: 1')
  await page.goto('/runs/id-metrics-partial')
  await page.locator('.react-flow__node').click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Availability: partial; coverage reasons: invalid_record.')
  await expect(page.getByLabel('Selected execution details')).toContainText('output tokens: unknown (missing_end) [fixture]')
})
