import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join } from 'node:path'

let server: Server
const fullBase = 'a'.repeat(40), fullHead = 'b'.repeat(40)
const run = { ref: 'run', display_id: 'lineage-run', label: 'Recorded lineage', completeness: 'recorded', started_at: 1, review_acceptance: { state: 'accepted_full_range', base: fullBase, head: fullHead }, acceptance_summary: { checks: [], checkpoints: [], reviews: [], full_range: { state: 'accepted_full_range', base: fullBase, head: fullHead } } }
const snapshot = { runs: [run], phases: [], tasks: [], review_definitions: [], occurrences: [], records: [], unknown_records: [], edges: [], activities: [{ ref: 'fix-call', run_ref: run.ref, invocation_id: 'fix-call', occurrence_ref: 'fix-call-occ', task_ref: null, role: 'fixing_worker', invocation_kind: 'task_worker', outcome: 'returned', error_category: null, input_qualification: 'recorded', input_refs: [], correction_chain: ['fix-call'], support_ref: null, stopped_by_ref: null, record_refs: [] }], snapshot_ref: 'lineage', next_cursor: null, inventory: { phase_count: 0, occurrence_count: 3, observation_count: 0, total_count: 0, loaded_count: 0, hidden_count: 0, unsupported_count: 0 }, chain: [
  { ref: 'original-review', run_ref: run.ref, execution_id: 'original', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: [], review_range: { base: fullBase, head: fullBase }, findings: ['src/file.ts:1 - original rejection'], commit_refs: {} },
  { ref: 'fix', run_ref: run.ref, execution_id: 'fix', role: 'fixer', review_ordinal: null, fixing_round: 1, outcome: 'approved', trigger_ref: 'original-review', predecessor_ref: null, occurrence_refs: ['fix-call-occ'], review_range: { base: fullBase, head: fullHead }, findings: [], commit_refs: {} },
  { ref: 'rereview', run_ref: run.ref, execution_id: 'rereview', role: 'reviewer', review_ordinal: 2, fixing_round: null, outcome: 'approved', trigger_ref: 'fix', predecessor_ref: null, occurrence_refs: [], review_range: { base: fullBase, head: fullHead }, findings: [], commit_refs: {} }
] }
test.beforeAll(async () => { server = createServer(async (request, response) => { const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174'); if (url.pathname === '/api/monitor/v1/projects') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ projects: [{ ref: 'project', label: 'Fixture', recordings: [] }] })); return }; if (url.pathname.endsWith('/runs')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }; if (url.pathname.endsWith('/snapshot')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot)); return }; if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: [] })); return }; try { const file = url.pathname === '/' ? 'index.html' : url.pathname.slice(1); response.setHeader('content-type', { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[extname(file)] ?? 'application/octet-stream'); response.end(await readFile(join('dist', file))) } catch { response.statusCode = 404; response.end() } }); await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve)) })
test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))
test('pages selected and correction history without hiding rejection', async ({ page }) => {
  const record = (ref: string, runRef: string) => ({ ref, run_ref: runRef, occurrence_ref: 'occ', kind: 'passed', source_seq: 1, recorded_at: 1, exit_code: 0, finding_count: null, review_base: null, review_head: null })
  const related = { ...snapshot, runs: [{ ...run, ref: 'related' }], chain: [], activities: [], occurrences: [{ ref: 'occ', run_ref: 'related', role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['related-first'] }], records: [record('related-first', 'related')], snapshot_ref: 'related-snapshot', next_cursor: 'related-next' }
  await page.route('**/followups?*', route => route.fulfill({ json: { followups: [{ run_ref: 'run', source_run_ref: 'related', review_occurrence_ref: 'occ', resolution: 'resolved' }] } }))
  await page.route('**/snapshot', route => route.fulfill({ json: route.request().url().includes('/related/') ? related : { ...snapshot, records: [record('first', 'run')], next_cursor: 'next' } }))
  await page.route('**/history?*', route => {
    const linked = route.request().url().includes('/related/')
    return route.fulfill({ json: linked ? { ...related, records: [record('related-second', 'related')], next_cursor: null } : { ...snapshot, records: [record('second', 'run')], next_cursor: null } })
  })
  await page.goto('/')
  await page.locator('.react-flow__node[data-id="original-review"]').click()
  const details = page.getByLabel('Selected execution details')
  await expect(details.getByText('Verdict: Changes requested.')).toBeVisible()
  await expect(details.getByText('src/file.ts:1 - original rejection')).toBeVisible()
  await page.locator('summary').filter({ hasText: /^Recorded evidence$/ }).click()
  await page.getByRole('button', { name: 'Load more history' }).click()
  await page.getByRole('button', { name: 'Load correction history' }).click()
  await expect(page.getByRole('button', { name: /Load (more|correction) history/ })).toHaveCount(0)
  await page.getByText('Loaded history', { exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Related run history' })).toBeVisible()
})

test('keeps retained rejection and later fixing/review attempts distinct and inspectable', async ({ page }) => { await page.goto('/'); await expect(page.locator('.react-flow__node')).toHaveCount(3); await expect(page.locator('.react-flow__node[data-id="original-review"]')).toHaveClass(/success/); await expect(page.locator('.react-flow__node[data-id="fix-call"]')).toContainText('Corrective worker'); await page.locator('.react-flow__node[data-id="original-review"]').click(); const details = page.getByLabel('Selected execution details'); await expect(details).toContainText('Execution: returned — changes requested.'); await expect(details).toContainText('src/file.ts:1 - original rejection'); await details.getByText('Recorded history').click(); await expect(details).not.toContainText(fullBase); await expect(details).not.toContainText(fullHead); await page.locator('.react-flow__node[data-id="rereview"]').click(); await expect(details).toContainText('Verdict: Approved.'); await expect(details).toContainText('Full-range qualification: Full-range acceptance recorded.') })
