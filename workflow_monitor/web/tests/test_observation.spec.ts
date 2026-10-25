import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join } from 'node:path'

let server: Server
let snapshots = 0
const run = { ref: 'run_live', display_id: 'observed-run', label: 'Observed run', completeness: 'recorded', started_at: 0, runner_state: { state: 'live', reason: null } }
function view() {
  snapshots++
  const unavailable = snapshots > 1
  return { runs: [run], phases: [{ ref: 'phase', run_ref: run.ref, label: 'Worker' }], tasks: [], occurrences: [{ ref: 'occ', run_ref: run.ref, phase_ref: 'phase', task_ref: null, role: 'worker', outcome: null, completeness: 'incomplete', record_refs: ['record'] }], records: [{ ref: 'record', run_ref: run.ref, occurrence_ref: 'occ', kind: 'started', source_seq: 0, recorded_at: 0, exit_code: null, finding_count: null, review_base: null, review_head: null }], unknown_records: [], edges: [], snapshot_ref: 'snapshot_live', next_cursor: null, inventory: { phase_count: 1, occurrence_count: 1, observation_count: 1, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 0 }, observation: { read_at: snapshots, last_success_at: 0, last_recorded_at: 0, read_state: unavailable ? 'unavailable' : 'current', warnings: unavailable ? ['read_unavailable', 'incomplete_history'] : ['incomplete_history'] } }
}
test.beforeAll(async () => {
  server = createServer(async (request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/projects') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ projects: [{ ref: 'project', label: 'Fixture', recordings: [] }] })); return }
    if (url.pathname.endsWith('/runs')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname.endsWith('/snapshot')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(view())); return }
    try { const file = url.pathname === '/' ? 'index.html' : url.pathname.slice(1); response.setHeader('content-type', { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[extname(file)] ?? 'application/octet-stream'); response.end(await readFile(join('dist', file))) } catch { response.statusCode = 404; response.end() }
  })
  await new Promise<void>(resolve => server.listen(4175, '127.0.0.1', resolve))
})
test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))
test('displays read freshness, incomplete history, and qualified liveness without control requests', async ({ page }) => {
  await page.clock.install(); await page.goto('http://127.0.0.1:4175/')
  await expect(page.getByLabel('Read freshness')).toContainText('last successful read 0; last recorded activity 0')
  await expect(page.getByLabel('Runner liveness')).toHaveText(/Recorded runner Live.*does not prove progress/)
  await page.clock.fastForward(60_000)
  await expect(page.getByLabel('Read freshness')).toContainText('Read unavailable')
  await expect(page.getByLabel('Read freshness')).toContainText('Read unavailable, Incomplete history')
})
