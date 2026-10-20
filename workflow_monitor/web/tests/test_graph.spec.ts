import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'

let server: Server
const snapshot = {
  runs: [{ ref: 'run_one', label: '<img src=x onerror=alert(1)> retained failure', completeness: 'recorded', started_at: 1 }, { ref: 'run_two', label: 'Second run', completeness: 'recorded', started_at: 2 }],
  phases: [{ ref: 'phase_one', run_ref: 'run_one', label: 'Worker' }, { ref: 'phase_two', run_ref: 'run_two', label: 'Review' }],
  tasks: [],
  occurrences: [{ ref: 'occ_failed', run_ref: 'run_one', phase_ref: 'phase_one', task_ref: null, role: 'worker', outcome: 'failed', completeness: 'complete', record_refs: ['record_one'] }, { ref: 'occ_reviewer', run_ref: 'run_two', phase_ref: 'phase_two', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: ['record_two'] }],
  records: [{ ref: 'record_one', run_ref: 'run_one', occurrence_ref: 'occ_failed', kind: 'failed', source_seq: 1, recorded_at: 1, exit_code: 1, finding_count: null, review_base: null, review_head: null }, { ref: 'record_two', run_ref: 'run_two', occurrence_ref: 'occ_reviewer', kind: 'passed', source_seq: 2, recorded_at: 2, exit_code: null, finding_count: 0, review_base: 'a'.repeat(40), review_head: 'b'.repeat(40) }],
  edges: [{ ref: 'edge_one', run_ref: 'run_one', type: 'phase_occurrence', from_ref: 'phase_one', to_ref: 'occ_failed', resolution: 'recorded' }, { ref: 'edge_two', run_ref: 'run_one', type: 'execution_milestone', from_ref: 'occ_failed', to_ref: 'record_one', resolution: 'recorded' }, { ref: 'edge_three', run_ref: 'run_two', type: 'phase_occurrence', from_ref: 'phase_two', to_ref: 'occ_reviewer', resolution: 'recorded' }],
  inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, hidden_count: 0 }
}

function selected(run: string) {
  return { ...snapshot, phases: snapshot.phases.filter(item => item.run_ref === run), occurrences: snapshot.occurrences.filter(item => item.run_ref === run), records: snapshot.records.filter(item => item.run_ref === run), edges: snapshot.edges.filter(item => item.run_ref === run), inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, hidden_count: 0 } }
}

test.beforeAll(async () => {
  server = createServer(async (request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: snapshot.runs })); return }
    const match = url.pathname.match(/^\/api\/monitor\/v1\/runs\/(run_(?:one|two))\/snapshot$/)
    if (match) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(selected(match[1]))); return }
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

test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))

test('switches selected production graph, selects details, and provides graph controls', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('button', { name: /retained failure/ })).toBeVisible()
  await expect(page.locator('img')).toHaveCount(0)
  await page.getByText('worker: failed').click()
  await expect(page.getByText('worker; failed')).toBeVisible()
  await page.getByRole('button', { name: /Second run/ }).click()
  await expect(page.getByText('reviewer: passed')).toBeVisible()
  await page.getByTitle('Zoom In').click()
  await expect(page.getByText('Inventory: 1 records, 1 occurrences, 1 phases; 0 hidden.')).toBeVisible()
})
