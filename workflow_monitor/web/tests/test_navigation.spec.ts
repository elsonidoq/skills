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
  throw new Error(`Production navigation fixture did not start: ${fixtureOutput}`)
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
test.afterAll(() => { fixture.kill('SIGTERM') })

test('uses actual production routes for display-ID direct opens, history, sorting, and local filtering', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL('/runs/id-...')
  await expect(page.getByLabel('Selected run')).toContainText('Run 1 — Recorded run')

  await page.getByLabel('Filter runs').fill('slash/%? #東京')
  await page.locator('.run-list button').click()
  await page.getByLabel('Filter runs').fill('')
  await expect(page).toHaveURL('/runs/id-slash%2F%25%3F%20%23%E6%9D%B1%E4%BA%AC')
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goBack()
  await expect(page).toHaveURL('/runs/id-...')
  await page.goForward()
  await expect(page).toHaveURL('/runs/id-slash%2F%25%3F%20%23%E6%9D%B1%E4%BA%AC')

  await page.getByLabel('Filter runs').fill('stopping')
  await expect(page.locator('.run-list button')).toHaveCount(1)
  await expect(page.getByText('The selected run is outside this filter.')).toBeVisible()
  await page.getByLabel('Filter runs').fill('no-such-run')
  await expect(page.getByText('No runs match this filter.')).toBeVisible()
  await page.getByLabel('Filter runs').fill('')

  await page.goto('/runs/id-...')
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goto('/runs/id-actual(run)')
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.reload()
  await expect(page).toHaveURL('/runs/id-actual(run)')
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goto('/runs/id-missing')
  await expect(page).toHaveURL('/runs/id-missing')
  await expect(page.getByRole('status')).toContainText('Run missing is unavailable.')
})
