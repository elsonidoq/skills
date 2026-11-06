import { test, expect } from '@playwright/test'
import { spawn, type ChildProcess } from 'node:child_process'
import { resolve } from 'node:path'
import { graphFor } from '../src/graph'

let fixture: ChildProcess
let output = ''
let project: { ref: string; recordings: Array<{ ref: string; label: string }> }
let projects: Array<{ ref: string; label: string }>
let runs: Array<{ ref: string; display_id: string; source: string; label: string; worktree_name: string | null }>
const headers = { 'X-Workflow-Monitor': '1', 'Sec-Fetch-Site': 'same-origin' }
const api = (suffix = '') => `http://127.0.0.1:4174/api/monitor/v1/projects/${project.ref}/runs${suffix}`
const run = (source: string, id: string) => runs.find(item => item.source === source && item.display_id.slice(25) === id)!
const address = (source: string, id: string) => `/projects/${project.ref}/runs/id-${encodeURIComponent(run(source, id).display_id)}`

test.beforeAll(async () => {
  const web = resolve(import.meta.dirname, '..')
  fixture = spawn(resolve(web, '../.venv/bin/python'), ['-B', 'tests/execution_fixture.py'], {
    cwd: web, env: { ...process.env, MONITOR_MULTIPROJECT: '1', PYTHONDONTWRITEBYTECODE: '1', PYTHONPATH: `${resolve(web, '../..')}/runtime:${resolve(web, '../..')}/runtime/tests` },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  fixture.stdout?.on('data', data => { output += data.toString() })
  fixture.stderr?.on('data', data => { output += data.toString() })
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch('http://127.0.0.1:4174/api/monitor/v1/projects', { headers })
      if (response.ok) {
        const data = await response.json()
        projects = data.projects
        project = data.projects.find((item: { label: string }) => item.label === 'fixture')
        runs = (await (await fetch(api(), { headers })).json()).runs
        if (runs.length) return
      }
    } catch { /* bounded isolated fixture startup */ }
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  throw new Error(`Composed fixture unavailable: ${output}`)
})
test.afterAll(async () => {
  if (fixture.exitCode !== null) return
  const exited = new Promise<void>(resolve => fixture.once('exit', () => resolve()))
  fixture.kill('SIGTERM')
  await exited
})

test('actual CLI capture survives fixture source removal through ordinary project selector and unchanged viewer', async ({ page }) => {
  expect(output).toContain('CLI/readback/private-exclusion/main-source-index-bytes/source-removal verified')
  expect(projects).toHaveLength(2)
  expect(project.recordings.map(item => item.label).sort()).toEqual(['linked', 'main', 'preserved'])
  expect(new Set(runs.map(item => item.ref)).size).toBe(runs.length)
  await page.goto('/')
  const fixtureButton = page.locator('.project-list button').filter({ hasText: 'fixture ·' })
  await fixtureButton.click()
  await expect(page.getByLabel('Selected project', { exact: true })).toContainText('fixture')
  const select = async (source: string, id: string) => {
    await page.getByLabel('Filter runs').fill(run(source, id).display_id)
    await expect(page.locator('.run-list button')).toHaveCount(1)
    await page.locator('.run-list button').click()
    await expect(page).toHaveURL(address(source, id))
    await expect(page.getByLabel('Selected source')).toHaveText(`Source: ${source}`)
    const row = run(source, id)
    const heading = `${id} · ${row.worktree_name ?? 'Worktree name unavailable'} · ${row.display_id.slice(0, 24)}`
    await expect(page.locator('.run-list strong')).toHaveText(heading)
    await expect(page.getByLabel('Selected run')).toHaveText(heading)
    await page.getByLabel('Filter runs').fill('')
  }
  expect(run('linked', 'success').worktree_name).toBe('still registered linked worktree')
  expect(run('main', 'success').worktree_name).toBe('fixture')
  expect(run('preserved', 'success').worktree_name).toBeNull()
  await select('main', '0123456789abcdef0123456789abcdef')
  await select('linked', 'success')
  await page.locator('.react-flow__node').first().click()
  await expect(page.getByLabel('Selected execution details')).toContainText('Total tokens: 12')
  for (const source of ['main', 'preserved']) {
    await select(source, 'original')
    const snapshot = await (await fetch(api(`/${run(source, 'original').ref}/snapshot`), { headers })).json()
    const followups = await (await fetch(api(`/${run(source, 'original').ref}/followups?snapshot=${snapshot.snapshot_ref}`), { headers })).json()
    expect(followups.followups[0].resolution).toBe('resolved')
    const recordingRef = run(source, 'original').ref.split('.')[0]
    expect(followups.followups.every((item: { run_ref: string; source_run_ref: string }) => item.run_ref.startsWith(recordingRef + '.') && item.source_run_ref.startsWith(recordingRef + '.'))).toBe(true)
    const reviewer = snapshot.chain.find((item: { execution_id: string }) => item.execution_id === 'review-id')
    const reviewerNode = graphFor(snapshot, [], []).nodes.find(item => item.data.identity?.executionId === reviewer.execution_id)!
    await page.locator(`.react-flow__node[data-id="${reviewerNode.id}"]`).click()
    await expect(page.getByLabel('Selected execution details')).toContainText('tracked:1 - retained original rejection')
    await select(source, 'engine-correction')
    await page.locator('.react-flow__node').filter({ hasText: 'Fix 1' }).click()
    await expect(page.getByLabel('Selected execution details')).toContainText('Total tokens: 12')
    await expect(page.getByLabel('Selected execution details')).toContainText('Corrective worker')
    await select(source, 'answered-paged')
    await page.getByRole('button', { name: 'Load more history', exact: true }).click()
    await expect(page.getByText(/Inventory: 52 total, 52 loaded, 0 hidden/)).toBeVisible()
    await select(source, 'metrics-partial')
    await page.locator('.react-flow__node').first().click()
    await expect(page.getByLabel('Selected execution details')).toContainText('Partial recorded coverage')
    await select(source, 'success')
    await page.locator('.react-flow__node').first().click()
    await expect(page.getByLabel('Selected execution details')).toContainText('Total tokens: 12')
    const data = await (await fetch(api(`/${run(source, 'success').ref}/snapshot`), { headers })).json()
    if (source === 'preserved') expect(data.runs.find((item: { ref: string }) => item.ref === run(source, 'success').ref).runner_state.state).toBe('unknown')
  }
  await page.reload()
  await expect(page.getByLabel('Selected source')).toHaveText('Source: preserved')
  await page.goto(address('preserved', 'slash/%? #東京'))
  await expect(page.getByLabel('Selected source')).toHaveText('Source: preserved')
  await page.reload()
  await expect(page).toHaveURL(address('preserved', 'slash/%? #東京'))
  await page.locator('.project-list button').filter({ hasText: 'second-project ·' }).click()
  await expect(page.getByLabel('Selected project', { exact: true })).toContainText('second-project')
  await expect(page.locator('.run-list button')).toHaveCount(1)
  await page.goBack()
  await expect(page).toHaveURL(address('preserved', 'slash/%? #東京'))
  await expect(page.getByLabel('Selected source')).toHaveText('Source: preserved')
  await page.goForward()
  await expect(page.getByLabel('Selected project', { exact: true })).toContainText('second-project')
})

test('qualifiers remain stable across filtering, polling and inventory changes', async ({ page }) => {
  await page.clock.install()
  let omitOthers = false
  await page.route(`**/api/monitor/v1/projects/${project.ref}/runs`, async route => {
    const response = await route.fetch({ headers: { ...route.request().headers(), 'sec-fetch-site': 'same-origin' } })
    const data = await response.json()
    await route.fulfill({ json: { ...data, runs: omitOthers ? data.runs.filter((item: { ref: string }) => item.ref === run('main', 'success').ref) : data.runs } })
  })
  await page.goto(address('main', 'success'))
  const heading = page.getByLabel('Selected run')
  await expect(heading).toContainText('success · fixture')
  const text = await heading.textContent()
  const qualifier = run('main', 'success').display_id.slice(0, 24)
  await page.getByLabel('Filter runs').fill(qualifier)
  await expect(page.locator('.run-list strong').filter({ hasText: text! })).toHaveCount(1)
  await page.getByLabel('Filter runs').fill('still registered linked worktree')
  await expect(page.getByText('The selected run is outside this filter.')).toBeVisible()
  await expect(heading).toHaveText(text!)
  omitOthers = true
  await page.getByLabel('Filter runs').fill('')
  await page.clock.fastForward(60_001)
  await expect(page.locator('.run-list button')).toHaveCount(1)
  await expect(heading).toHaveText(text!)
  await expect(page.locator('.run-list strong')).toHaveText(text!)
  expect(await page.locator('body').innerText()).not.toContain('/tmp/')
  expect(await page.locator('[title]').evaluateAll(elements => elements.map(element => element.getAttribute('title')).join(' '))).not.toContain('/tmp/')
})

test('recording switch invalidates delayed snapshot and same-run poll retains drag viewport and selection', async ({ page }) => {
  await page.clock.install()
  const main = run('main', 'success'), preserved = run('preserved', 'success')
  let release!: () => void
  const held = new Promise<void>(resolve => { release = resolve })
  let requested = false
  await page.route(`**/runs/${main.ref}/snapshot`, async route => {
    const response = await route.fetch()
    requested = true
    await held
    await route.fulfill({ response })
  })
  await page.goto(address('main', 'success'))
  await expect.poll(() => requested).toBe(true)
  await page.getByLabel('Filter runs').fill(preserved.display_id)
  await page.locator('.run-list button').click()
  await expect(page.getByLabel('Selected source')).toHaveText('Source: preserved')
  await expect(page.locator('.react-flow__node').first()).toBeVisible()
  release()
  await expect(page.locator('.react-flow__node').first()).toHaveAttribute('data-id', new RegExp(preserved.ref.split('.')[0] + '\\.'))
  const node = page.locator('.react-flow__node').first()
  const box = (await node.boundingBox())!
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down(); await page.mouse.move(box.x + box.width / 2 + 35, box.y + box.height / 2 + 25, { steps: 5 }); await page.mouse.up()
  await node.click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toBeVisible()
  const viewport = page.locator('.react-flow__viewport')
  const transform = await viewport.getAttribute('style')
  const position = await node.evaluate(element => (element as HTMLElement).style.transform)
  let polls = 0
  page.on('response', response => { if (response.url().includes(`/runs/${preserved.ref}/snapshot`)) polls++ })
  await page.clock.fastForward(60_001)
  await expect.poll(() => polls).toBeGreaterThan(0)
  await expect(viewport).toHaveAttribute('style', transform!)
  await expect.poll(() => node.evaluate(element => (element as HTMLElement).style.transform)).toBe(position)
  await expect(details).toContainText('Total tokens: 12')
})
