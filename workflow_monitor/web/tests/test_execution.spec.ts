import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join } from 'node:path'

let server: Server
const run = { ref: 'run_details', display_id: 'details-run', label: 'Recorded run', completeness: 'recorded', started_at: 1, acceptance_summary: { checks: [], checkpoints: [], reviews: [{ occurrence_ref: 'review-occurrence', state: 'rejected', approved: false, finding_count: 1, base: 'a'.repeat(40), head: 'b'.repeat(40) }], full_range: { state: 'unknown', base: null, head: null } } }
const snapshot = {
  runs: [run], phases: [], review_definitions: [], unknown_records: [], edges: [], chain: [], snapshot_ref: 'details-snapshot', next_cursor: null,
  tasks: [{ ref: 'task', run_ref: run.ref, task_id: 'T006', label: 'Task', summary: '<img src=x onerror=alert(1)> Display selected activity details', prerequisite_refs: [] }],
  occurrences: [{ ref: 'stop', run_ref: run.ref, phase_ref: 'terminal', task_ref: null, role: 'non_model', outcome: 'failed', completeness: 'complete', record_refs: [], stopping: true, support_ref: 'worker' }],
  records: [{ ref: 'record', run_ref: run.ref, occurrence_ref: 'worker-occurrence', kind: 'returned', source_seq: 3, recorded_at: 3, exit_code: 0, finding_count: null, review_base: null, review_head: null }],
  activities: [{ ref: 'worker', run_ref: run.ref, invocation_id: 'invocation-1', occurrence_ref: 'worker-occurrence', task_ref: 'task', role: 'worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: [], support_ref: null, stopped_by_ref: 'stop', record_refs: ['record'] }],
  inventory: { phase_count: 0, occurrence_count: 2, observation_count: 1, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 0 },
}

test.beforeAll(async () => {
  server = createServer(async (request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname.endsWith('/snapshot')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot)); return }
    if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: [] })); return }
    try { const file = url.pathname === '/' ? 'index.html' : url.pathname.slice(1); response.setHeader('content-type', { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[extname(file)] ?? 'application/octet-stream'); response.end(await readFile(join('dist', file))) } catch { response.statusCode = 404; response.end() }
  })
  await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve))
})
test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))

test('renders selected actual activity details with human-first outcome and inert retained text', async ({ page }) => {
  await page.goto('/')
  const worker = page.locator('.react-flow__node[data-id="worker"]')
  await expect(worker).toContainText('Display selected activity details')
  await worker.click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Display selected activity details')
  await expect(details).toContainText('Execution outcome: returned — acceptance not established.')
  await expect(details).toContainText('What happened: not recorded.')
  await expect(details).toContainText('Stopping reason: Recorded stopping reference stop.')
  await expect(details.locator('img')).toHaveCount(0)
  await expect(details.getByText('Invocation ID: invocation-1')).not.toBeVisible()
  await details.getByText('Technical references and retained history').click()
  await expect(details.getByText('Invocation ID: invocation-1')).toBeVisible()
  await expect(details).toContainText('returned; sequence 3; recorded 3; exit 0')
  await expect(details).toContainText('Full-range qualification: unknown.')
})
