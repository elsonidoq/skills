import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { readFile } from 'node:fs/promises'
import { extname, join } from 'node:path'

let server: Server
const fullBase = 'a'.repeat(40), fullHead = 'b'.repeat(40)
const runs = [
  { ref: 'original', label: 'Original rejected run', completeness: 'recorded', started_at: 1, review_acceptance: { state: 'accepted_full_range', base: fullBase, head: fullHead } },
  { ref: 'fixing', label: 'Declared fixing run', completeness: 'recorded', started_at: 2, review_acceptance: { state: 'accepted_full_range', base: fullBase, head: fullHead } },
  { ref: 'correction_only', label: 'Correction-only run', completeness: 'recorded', started_at: 3, review_acceptance: { state: 'correction_only', base: fullBase, head: 'c'.repeat(40) } },
  { ref: 'unrelated', label: 'Unrelated run', completeness: 'recorded', started_at: 4, review_acceptance: { state: 'unknown', base: null, head: null } },
]
function occurrence(ref: string, run_ref: string, role: string, outcome: string, phase_ref = `phase_${ref}`) { return { ref, run_ref, phase_ref, task_ref: null, role, outcome, completeness: 'complete', record_refs: [`record_${ref}`] } }
function record(ref: string, run_ref: string, occurrence_ref: string, kind: string, seq: number, base: string | null = null, head: string | null = null) { return { ref, run_ref, occurrence_ref, kind, source_seq: seq, recorded_at: seq, exit_code: null, finding_count: kind === 'failed' ? 1 : 0, review_base: base, review_head: head } }
const original = { ...occurrence('original_review', 'original', 'reviewer', 'failed'), execution_summary: { state: 'success', qualification: null } }
const fixing = { ...occurrence('fixing_worker', 'fixing', 'fixing_worker', 'passed'), task_ref: 'task_fix' }
const check = occurrence('fixing_check', 'fixing', 'non_model', 'passed')
const checkpoint = occurrence('fixing_checkpoint', 'fixing', 'non_model', 'passed')
const rereview = occurrence('fixing_rereview', 'fixing', 'reviewer', 'passed')
const byRun: Record<string, any> = {
  original: { occurrences: [original], records: [record('record_original_review', 'original', original.ref, 'failed', 1, fullBase, fullBase)], edges: [{ ref: 'original_edge', run_ref: 'original', type: 'execution_milestone', from_ref: original.ref, to_ref: 'record_original_review', resolution: 'recorded' }] },
  fixing: { occurrences: [fixing, check, checkpoint, rereview], records: [record('record_fixing_worker', 'fixing', fixing.ref, 'passed', 2), record('record_fixing_check', 'fixing', check.ref, 'passed', 3), record('record_fixing_checkpoint', 'fixing', checkpoint.ref, 'passed', 4), record('record_fixing_rereview', 'fixing', rereview.ref, 'passed', 5, fullBase, fullHead)], edges: [{ ref: 'fix_check', run_ref: 'fixing', type: 'recorded_next', from_ref: fixing.ref, to_ref: check.ref, resolution: 'recorded' }, { ref: 'check_checkpoint', run_ref: 'fixing', type: 'recorded_next', from_ref: check.ref, to_ref: checkpoint.ref, resolution: 'recorded' }, { ref: 'checkpoint_review', run_ref: 'fixing', type: 'recorded_next', from_ref: checkpoint.ref, to_ref: rereview.ref, resolution: 'recorded' }] },
  correction_only: { occurrences: [], records: [], edges: [] },
}
function snapshot(run: string) { const data = byRun[run]; return { runs, phases: [], tasks: [{ ref: 'task_fix', run_ref: 'fixing', label: 'T001', summary: 'Offline correction fixture' }], ...data, unknown_records: [{ ref: `unknown_${run}`, run_ref: run, source_seq: 99, code: 'unsupported_observation' }], snapshot_ref: `snapshot_${run}`, next_cursor: null, inventory: { phase_count: 0, occurrence_count: data.occurrences.length, observation_count: data.records.length, total_count: data.records.length + 1, loaded_count: data.records.length + 1, hidden_count: 0, unsupported_count: 1 } } }
const relations = [{ run_ref: 'fixing', source_run_ref: 'original', review_occurrence_ref: 'original_review', resolution: 'resolved' }, { run_ref: 'correction_only', source_run_ref: 'original', review_occurrence_ref: 'original_review', resolution: 'unresolved' }, { run_ref: 'cyclic', source_run_ref: 'original', review_occurrence_ref: 'original_review', resolution: 'cyclic' }]

test.beforeAll(async () => { server = createServer(async (request, response) => { const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174'); if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs })); return }; const match = url.pathname.match(/^\/api\/monitor\/v1\/runs\/(original|fixing|correction_only)\/snapshot$/); if (match) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot(match[1]))); return }; if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: relations })); return }; try { const file = url.pathname === '/' ? 'index.html' : url.pathname.slice(1); response.setHeader('content-type', { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[extname(file)] ?? 'application/octet-stream'); response.end(await readFile(join('dist', file))) } catch { response.statusCode = 404; response.end() } }); await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve)) })
test.afterAll(() => new Promise<void>(resolve => server.close(() => resolve())))

test('navigates an explicit reviewer-to-fixing-to-rereview lineage without replacing the rejected root', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.react-flow__node:not(.owner-group)')).toHaveCount(3)
  await expect(page.locator('.react-flow__node[data-id="original_review"]')).toHaveClass(/success/)
  await expect(page.locator('.react-flow__node[data-id="fixing_worker"]')).toContainText('Fixing worker attempt unknown')
  await expect(page.locator('.react-flow__node[data-id="fixing_rereview"]')).toHaveClass(/success/)
  await expect(page.locator('.react-flow__node[data-id="fixing_check"]')).toHaveCount(0)
  await page.locator('.react-flow__node[data-id="fixing_rereview"]').click()
  await expect(page.getByLabel('Selected execution details')).toContainText(`range ${fullBase} → ${fullHead}`)
  await expect(page.locator('.react-flow__node[data-id="fixing_rereview"]')).toHaveClass(/selected/)
  await expect(page.locator('.react-flow__node[data-id="original_review"]')).toHaveClass(/success/)
  await expect(page.getByLabel('Lineage acceptance')).toHaveText(`Full-range acceptance: ${fullBase} → ${fullHead}`)
  await expect(page.getByText('resolved: original → fixing')).toBeVisible()
  const correctionEdge = page.getByTestId('rf__edge-followup_original_review_fixing_worker')
  await expect(correctionEdge).toHaveAttribute('aria-label', 'Edge from original_review to fixing_worker')
  await correctionEdge.dispatchEvent('click')
  await expect(page.getByLabel('Selected execution details')).toContainText('Declared cross-run correction')
  await expect(page.getByLabel('Selected execution details')).toContainText('declared cross-run correction; not recorded exact execution causality')
  await expect(page.getByText('unresolved: original → correction_only')).toBeVisible()
  await expect(page.getByText('cyclic: original → cyclic')).toBeVisible()
  await page.getByText('Loaded history and technical references').click(); await expect(page.getByText(/unsupported unsupported_observation; unknown_original/)).toBeVisible()
  await expect(page.getByText('Inventory: 2 total, 2 loaded, 0 hidden, 1 unsupported.')).toBeVisible()
  await page.getByRole('button', { name: /Correction-only run/ }).click()
  await expect(page.getByLabel('Lineage acceptance')).toHaveText('Correction-only review; current head is not accepted.')
})
