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

test('distinguishes an unavailable recording inventory from an empty one', async ({ page }) => {
  let unavailable = true
  await page.route(`**/api/monitor/v1/projects/${projectRef}/runs`, route => route.fulfill({ json: {
    monitor_version: 1, runs: [], next_cursor: null,
    unavailable_recordings: unavailable ? [{ ref: 'recording_fixture', label: 'main' }] : []
  } }))
  await page.goto('/')
  await expect(page.getByRole('status')).toHaveText('Recorded monitor data is unavailable.')
  unavailable = false
  await page.reload()
  await expect(page.getByRole('status')).toHaveText('No recorded runs are available.')
})

for (const source of ['linked', 'main'] as const) {
  test(`keeps ${source === 'linked' ? 'mixed-source' : 'cached-row'} availability failures visible beside a selected run and clears them on recovery`, async ({ page }) => {
    await page.clock.install()
    let unavailable = true
    await page.route(`**/api/monitor/v1/projects/${projectRef}/runs`, async route => {
      const response = await route.fetch({ headers: { ...route.request().headers(), 'sec-fetch-site': 'same-origin' } })
      const data = await response.json()
      expect(response.status()).toBe(200)
      expect(Array.isArray(data.runs)).toBe(true)
      await route.fulfill({ json: { ...data, unavailable_recordings: unavailable
        ? [{ ref: source === 'main' ? `recording_${mainQualifier}` : 'recording_failed_linked', label: source }] : [] } })
    })
    await page.goto(runPage('success'))
    await expect(page.getByRole('status')).toHaveText('Updated from the recorded snapshot.')
    const warning = page.getByRole('alert', { name: 'Recording availability' })
    await expect(warning).toContainText(`unavailable for ${source}`)
    await expect(warning).toContainText('last-safe data')
    await expect(page.locator('.react-flow__node').first()).toBeVisible()
    // Snapshot success and subsequent same-run polling cannot erase source failures.
    await page.clock.fastForward(60_001)
    await expect(warning).toBeVisible()
    unavailable = false
    await page.clock.fastForward(60_001)
    await expect(warning).toHaveCount(0)
    await expect(page).toHaveURL(runPage('success'))
    await expect(page.locator('.react-flow__node').first()).toBeVisible()
  })
}

test('uses actual production routes for display-ID direct opens, history, sorting, and local filtering', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL(runPage('...'))
  await expect(page.getByLabel('Selected run')).toHaveText(`... · fixture · ${mainQualifier}`)

  await page.getByLabel('Filter runs').fill('slash/%? #東京')
  await page.locator('.run-list button').click()
  await page.getByLabel('Filter runs').fill('')
  await expect(page).toHaveURL(runPage('slash/%? #東京'))
  await expect(page.getByLabel('Selected run')).toContainText('Run identifier unavailable · fixture')
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
  await expect(page.getByLabel('Selected run')).toContainText('... · fixture')
  await page.goto(runPage('actual(run)'))
  await expect(page.getByLabel('Selected run')).toContainText('actual(run) · fixture')
  await page.reload()
  await expect(page).toHaveURL(runPage('actual(run)'))
  await expect(page.getByLabel('Selected run')).toContainText('actual(run) · fixture')
  await page.goto(runPage('missing'))
  await expect(page).toHaveURL(runPage('missing'))
  await expect(page.getByRole('status')).toHaveText('The selected run is unavailable.')
})
