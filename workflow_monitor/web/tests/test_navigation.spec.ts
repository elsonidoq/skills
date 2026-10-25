import { test, expect } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'
import { resolve } from 'node:path'

let fixture: ChildProcess
let fixtureOutput = ''
let projectRef = ''
let mainQualifier = ''
const runPage = (id: string) => `/projects/${encodeURIComponent(projectRef)}/runs/id-${encodeURIComponent(`${mainQualifier}-${id}`)}`

async function ready() {
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch('http://127.0.0.1:4174/api/monitor/v1/projects', { headers: { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' } })
      if (response.ok) { const project = (await response.json()).projects[0]; projectRef = project?.ref ?? ''; mainQualifier = project?.recordings.find((item: { label: string }) => item.label === 'main')?.ref.split('_')[1] ?? ''; if (projectRef) return }
    } catch { /* fixture is still starting */ }
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  throw new Error(`Production navigation fixture did not start: ${fixtureOutput}`)
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

test('uses actual production routes for display-ID direct opens, history, sorting, and local filtering', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL(runPage('...'))
  await expect(page.getByLabel('Selected run')).toContainText('Run 1 — Recorded run')

  await page.getByLabel('Filter runs').fill('slash/%? #東京')
  await page.locator('.run-list button').click()
  await page.getByLabel('Filter runs').fill('')
  await expect(page).toHaveURL(runPage('slash/%? #東京'))
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goBack()
  await expect(page).toHaveURL(runPage('...'))
  await page.goForward()
  await expect(page).toHaveURL(runPage('slash/%? #東京'))

  await page.getByLabel('Filter runs').fill('stopping')
  await expect(page.locator('.run-list button')).toHaveCount(1)
  await expect(page.getByText('The selected run is outside this filter.')).toBeVisible()
  await page.getByLabel('Filter runs').fill('no-such-run')
  await expect(page.getByText('No runs match this filter.')).toBeVisible()
  await page.getByLabel('Filter runs').fill('')

  await page.goto(runPage('...'))
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goto(runPage('actual(run)'))
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.reload()
  await expect(page).toHaveURL(runPage('actual(run)'))
  await expect(page.getByLabel('Selected run')).toContainText('Recorded run')
  await page.goto(runPage('missing'))
  await expect(page).toHaveURL(runPage('missing'))
  await expect(page.getByRole('status')).toContainText(`Run ${mainQualifier}-missing is unavailable.`)
})
