import { test, expect } from '@playwright/test'
import { createServer, type Server } from 'node:http'
import { createServer as createViteServer, type ViteDevServer } from 'vite'
import { layoutFootprints, type FootprintLayoutInput } from '../src/layout'

let server: Server
let vite: ViteDevServer
let fixtureStage: 'base' | 'overlay' | 'content' = 'base'
const sha = (value: string) => value.repeat(40)
const longHostileLabel = '<img src=x onerror=alert(1)> retained task label that is deliberately longer than eighty characters for Details'
const refreshedTaskTitle = 'Repeated generic branch'
const refreshedBlocker = 'A refreshed blocker annotation that is deliberately long enough to wrap in the graph node and require an intrinsic measurement'
const run = { ref: 'run_chain', display_id: 'chain-fixture', label: 'Synthetic recorded chain', completeness: 'recorded', started_at: 1, plan_availability: 'complete', acceptance_summary: { checks: [], checkpoints: [], reviews: [], full_range: { state: 'accepted_full_range', base: sha('a'), head: sha('c') } } }
const tasks = [
  { ref: 'task_a', run_ref: run.ref, task_id: 'A', label: longHostileLabel, summary: 'Synthetic branch root', prerequisite_refs: [], progress: { state: 'completed', qualification: null } },
  { ref: 'task_b', run_ref: run.ref, task_id: 'B', label: 'Task', summary: 'Repeated generic branch', prerequisite_refs: ['task_a'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_c', run_ref: run.ref, task_id: 'C', label: 'Task', summary: 'Repeated generic branch', prerequisite_refs: ['task_a'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_e', run_ref: run.ref, task_id: 'E', label: 'Task', summary: 'Repeated generic branch', prerequisite_refs: ['task_a'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_d', run_ref: run.ref, task_id: 'D', label: 'Task', summary: 'Joining completed branches', prerequisite_refs: ['task_b', 'task_c'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_f', run_ref: run.ref, task_id: 'F', label: 'Task', summary: 'Transitive completion after the join', prerequisite_refs: ['task_d', 'task_e'], progress: { state: 'completed', qualification: null } },
  { ref: 'task_pending', run_ref: run.ref, task_id: 'P', label: 'Task', summary: 'Independent pending work', prerequisite_refs: [], progress: { state: 'pending', qualification: null } },
]
const chain = [
  { ref: 'review_one', run_ref: run.ref, execution_id: 'review_one', role: 'reviewer', review_ordinal: 1, fixing_round: null, outcome: 'rejected', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['occ_review_one'], review_range: { base: sha('a'), head: sha('b') }, findings: ['src/example.ts:7 - synthetic rejection'], commit_refs: { base: sha('a'), head: sha('b') } },
  { ref: 'fix_one', run_ref: run.ref, execution_id: 'fix_one', role: 'fixer', review_ordinal: null, fixing_round: 1, outcome: 'approved', trigger_ref: 'review_one', predecessor_ref: 'review_one', occurrence_refs: ['occ_fix'], review_range: { base: sha('a'), head: sha('c') }, findings: [], commit_refs: { commit: sha('c') } },
  { ref: 'review_two', run_ref: run.ref, execution_id: 'review_two', role: 'reviewer', review_ordinal: 2, fixing_round: null, outcome: 'approved', trigger_ref: null, predecessor_ref: 'fix_one', occurrence_refs: ['occ_review_two'], review_range: { base: sha('a'), head: sha('c') }, findings: [], commit_refs: { head: sha('c') } },
  { ref: 'dangling_review', run_ref: run.ref, execution_id: 'dangling_review', role: 'reviewer', review_ordinal: 3, fixing_round: null, outcome: 'unknown', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['missing_occurrence'], review_range: { base: null, head: null }, findings: [], commit_refs: {} },
  { ref: 'conflicting_fixer', run_ref: run.ref, execution_id: 'conflicting_fixer', role: 'fixer', review_ordinal: null, fixing_round: 2, outcome: 'unknown', trigger_ref: null, predecessor_ref: null, occurrence_refs: ['missing_b_attempt', 'missing_c_attempt'], review_range: { base: null, head: null }, findings: [], commit_refs: {} },
]
function snapshot() {
  const refreshed = fixtureStage === 'content'
  const secondaryOverlay = fixtureStage === 'overlay'
  const refreshedTasks = refreshed ? tasks.map(task => task.ref === 'task_b' ? { ...task, summary: refreshedTaskTitle, annotation: { code: 'blocked', label: refreshedBlocker } } : task) : tasks
  const rereview = refreshed ? { ...chain[2], outcome: 'rejected' as const, findings: ['src/example.ts:9 - refreshed outcome', 'src/example.ts:10 - refreshed outcome'] } : chain[2]
  return {
    runs: [run], phases: [], tasks: refreshedTasks, review_definitions: [{ ref: 'planned_review', run_ref: run.ref, label: 'Planned independent review definition' }], chain: [chain[0], chain[1], rereview, chain[3], chain[4]], chain_acceptance: {},
    occurrences: [
      { ref: 'worker_a', run_ref: run.ref, phase_ref: 'worker', task_ref: 'task_a', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'occ_review_one', run_ref: run.ref, phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'occ_fix', run_ref: run.ref, phase_ref: 'worker', task_ref: 'task_d', role: 'fixing_worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'fix_check', run_ref: run.ref, phase_ref: 'check', task_ref: 'task_d', role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['record_check'] },
      { ref: 'fix_checkpoint', run_ref: run.ref, phase_ref: 'checkpoint', task_ref: 'task_d', role: 'non_model', outcome: 'passed', completeness: 'complete', record_refs: ['record_checkpoint'] },
      { ref: 'occ_review_two', run_ref: run.ref, phase_ref: 'review', task_ref: null, role: 'reviewer', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'task_b_attempt_one', run_ref: run.ref, occurrence_id: '1', phase_ref: 'worker', task_ref: 'task_b', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
      { ref: 'task_b_attempt_two', run_ref: run.ref, occurrence_id: '2', phase_ref: 'worker', task_ref: 'task_b', role: 'worker', outcome: 'failed', completeness: 'complete', record_refs: [] },
      { ref: 'task_c_attempt', run_ref: run.ref, phase_ref: 'worker', task_ref: 'task_c', role: 'worker', outcome: 'passed', completeness: 'complete', record_refs: [] },
    ],
    records: [], unknown_records: [{ ref: 'legacy_unknown', run_ref: run.ref, source_seq: 99, code: 'unsupported_observation' }],
    edges: [
      { ref: 'trigger', run_ref: run.ref, type: 'chain_trigger', from_ref: 'review_one', to_ref: 'fix_one', resolution: 'recorded' },
      { ref: 'check', run_ref: run.ref, type: 'chain_check', from_ref: 'fix_one', to_ref: 'record_check', resolution: 'recorded' },
      { ref: 'checkpoint', run_ref: run.ref, type: 'chain_checkpoint', from_ref: 'fix_one', to_ref: 'record_checkpoint', resolution: 'recorded' },
      { ref: 'predecessor', run_ref: run.ref, type: 'chain_predecessor', from_ref: 'fix_one', to_ref: 'review_two', resolution: 'recorded' },
      ...(secondaryOverlay ? [{ ref: 'eligible_secondary_overlay', run_ref: run.ref, type: 'chain_predecessor', from_ref: 'review_one', to_ref: 'review_two', resolution: 'recorded' }] : []),
    ],
    snapshot_ref: 'chain_snapshot', next_cursor: null,
    inventory: { phase_count: 0, occurrence_count: 9, observation_count: 0, total_count: 1, loaded_count: 1, hidden_count: 0, unsupported_count: 1 },
  }
}

test.beforeAll(async () => {
  vite = await createViteServer({ server: { middlewareMode: true }, appType: 'spa' })
  server = createServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://127.0.0.1:4174')
    if (url.pathname === '/api/monitor/v1/runs') { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ runs: [run] })); return }
    if (url.pathname === '/fixture-stage') { fixtureStage = (url.searchParams.get('value') === 'overlay' ? 'overlay' : url.searchParams.get('value') === 'content' ? 'content' : 'base'); response.end('ok'); return }
    if (url.pathname === `/api/monitor/v1/runs/${run.ref}/snapshot`) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify(snapshot())); return }
    if (url.pathname.endsWith('/followups')) { response.setHeader('content-type', 'application/json'); response.end(JSON.stringify({ followups: [] })); return }
    vite.middlewares(request, response, () => { response.statusCode = 404; response.end() })
  })
  await new Promise<void>(resolve => server.listen(4174, '127.0.0.1', resolve))
})
test.afterAll(async () => { await new Promise<void>(resolve => server.close(() => resolve())); await vite.close() })

test('renders a measured multilevel recorded chain without changing its backbone for secondary overlays', async ({ page }, testInfo) => {
  await page.clock.install()
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  const graph = page.getByLabel('Workflow graph')
  const owners: Record<string, string> = { worker_a: 'task_a', task_b_attempt_one: 'task_b', task_b_attempt_two: 'task_b', task_c_attempt: 'task_c', fix_one: 'task_d', fix_check: 'task_d', fix_checkpoint: 'task_d', planned_review: 'run-review', review_one: 'run-review', review_two: 'run-review', dangling_review: 'unassigned-history', conflicting_fixer: 'unassigned-history' }
  const prerequisitePairs = [['task_a', 'task_b'], ['task_a', 'task_c'], ['task_a', 'task_e'], ['task_b', 'task_d'], ['task_c', 'task_d'], ['task_d', 'task_f'], ['task_e', 'task_f']] as const
  const readGeometry = () => page.evaluate((ownerMap) => {
    const position = (element: HTMLElement) => {
      const match = element.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)/)
      return { x: Number(match?.[1] ?? 0), y: Number(match?.[2] ?? 0), width: element.offsetWidth, height: element.offsetHeight }
    }
    return [...document.querySelectorAll<HTMLElement>('.react-flow__node[data-id]')].map(element => {
      const id = element.dataset.id!
      const bounds = position(element)
      const measured = (item: HTMLElement) => { const horizontalBorder = item.offsetWidth - item.clientWidth; const verticalBorder = item.offsetHeight - item.clientHeight; return { width: Math.max(item.offsetWidth, item.scrollWidth + horizontalBorder), height: Math.ceil(Math.max(item.offsetHeight, item.scrollHeight + verticalBorder)) } }
      const header = element.querySelector<HTMLElement>('[data-group-header]')
      return { id, bounds, cssBounds: { x: bounds.x, y: bounds.y, width: Number.parseFloat(element.style.width), height: Number.parseFloat(element.style.height) }, measurement: measured(element), owner: ownerMap[id] ?? (id.startsWith('task_') ? id : null), header: header ? { x: bounds.x + header.offsetLeft, y: bounds.y + header.offsetTop, ...measured(header) } : null }
    })
  }, owners)
  const assertMeasuredLayout = async () => {
    await page.clock.fastForward(1)
    await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(() => resolve())))))
    const actual = await readGeometry()
    const groups = actual.filter(item => item.id.startsWith('group:'))
    const input: FootprintLayoutInput = {
      groups: groups.map(group => ({ id: group.id.slice(6), kind: group.id.slice(6) === 'run-review' ? 'run-review' as const : group.id.slice(6) === 'unassigned-history' ? 'unassigned' as const : 'task' as const, header: { width: group.header!.width, height: group.header!.height }, members: actual.filter(item => item.owner === group.id.slice(6)).map(item => ({ id: item.id, size: { width: item.cssBounds.width, height: item.cssBounds.height } })) })),
      prerequisites: prerequisitePairs.map(([source, target]) => ({ source, target })),
    }
    const expected = await layoutFootprints(input)
    const expectedGroups = new Map(expected.groups.map(group => [group.id, group]))
    const actualGroups = new Map(groups.map(group => [group.id.slice(6), group]))
    const contains = (outer: typeof actual[number]['bounds'], inner: typeof actual[number]['bounds']) => inner.x >= outer.x && inner.y >= outer.y && inner.x + inner.width <= outer.x + outer.width && inner.y + inner.height <= outer.y + outer.height
    const overlaps = (one: typeof actual[number]['bounds'], two: typeof actual[number]['bounds']) => one.x < two.x + two.width && two.x < one.x + one.width && one.y < two.y + two.height && two.y < one.y + one.height
    const expectBounds = (observed: { x: number; y: number; width: number; height: number }, expectedBounds: { x: number; y: number; width: number; height: number }, message: string) => { expect(observed.x, `${message} x`).toBeCloseTo(expectedBounds.x, 1); expect(observed.y, `${message} y`).toBeCloseTo(expectedBounds.y, 1); expect(observed.width, `${message} width`).toBe(expectedBounds.width); expect(observed.height, `${message} height`).toBe(expectedBounds.height) }
    for (const group of expected.groups) {
      const observed = actualGroups.get(group.id)!
      expectBounds(observed.cssBounds, group.bounds, `${group.id} group CSS bounds`)
      expectBounds(observed.header!, group.header, `${group.id} header bounds`)
      expect(contains(observed.cssBounds, observed.header!), `${group.id} header fits owner`).toBeTruthy()
      for (const child of group.children) {
        const observedChild = actual.find(item => item.id === child.id)!
        expectBounds(observedChild.cssBounds, child.bounds, `${child.id} CSS dimensions and graph-coordinate bounds`)
        expect(contains(observed.cssBounds, observedChild.cssBounds), `${child.id} fits ${group.id}`).toBeTruthy()
        expect(overlaps(observed.header!, observedChild.bounds), `${group.id} header does not overlap ${child.id}`).toBeFalsy()
      }
    }
    for (let index = 0; index < groups.length; index++) for (let other = index + 1; other < groups.length; other++) expect(overlaps(groups[index].cssBounds, groups[other].cssBounds), `${groups[index].id} and ${groups[other].id} do not overlap`).toBeFalsy()
    for (const [source, target] of prerequisitePairs) expect(actualGroups.get(target)!.cssBounds.y, `${target} is below ${source}`).toBeGreaterThanOrEqual(actualGroups.get(source)!.cssBounds.y + actualGroups.get(source)!.cssBounds.height)
    console.log(`Observed graph bounds: ${JSON.stringify(actual.map(item => ({ id: item.id, bounds: item.cssBounds, header: item.header })) )}`)
    return actual
  }

  for (const id of tasks.map(task => task.ref)) await expect(page.locator(`.react-flow__node[data-id="${id}"]`)).toHaveCount(1)
  for (const [source, target] of prerequisitePairs) await expect(page.getByTestId(`rf__edge-dependency_${source}_${target}`)).toHaveCount(1)
  await expect(page.locator('.react-flow__node[data-id="task_pending"]')).toContainText('Independent pending work')
  await expect(page.locator('.react-flow__node[data-id="task_b_attempt_one"]')).toContainText('attempt 1')
  await expect(page.locator('.react-flow__node[data-id="task_b_attempt_two"]')).toContainText('attempt 2')
  await expect(page.locator('.react-flow__node[data-id="task_b_attempt_two"]')).toContainText('failed')
  await expect(page.locator('.react-flow__node[data-id="review_one"]')).toContainText('Review 1')
  await expect(page.locator('.react-flow__node[data-id="fix_one"]')).toContainText('Fixing agent')
  await expect(page.locator('.react-flow__node[data-id="review_two"]')).toContainText('Review 2')
  await expect(page.locator('.react-flow__node[data-id="planned_review"]')).toContainText('Planned independent review definition')
  await expect(page.locator('.react-flow__node[data-id="group:run-review"]')).toContainText('Run review / execution history')
  await expect(page.locator('.react-flow__node[data-id="group:unassigned-history"]')).toContainText('Unassigned recorded history')
  await expect(page.getByTestId('rf__edge-trigger')).toBeVisible()
  for (const id of ['check', 'checkpoint']) await expect(page.getByTestId(`rf__edge-${id}`)).toHaveAttribute('aria-label', new RegExp(`Edge from fix_one to fix_${id}`))
  const overviewGeometry = await readGeometry()
  const overview = testInfo.outputPath('readable-chain-overview.png')
  await page.screenshot({ path: overview })
  console.log(`Overview chain screenshot: ${overview}`)

  await page.locator('.react-flow__node[data-id="review_one"]').click()
  const details = page.getByLabel('Selected execution details')
  await expect(details).toContainText('Execution outcome: rejected')
  await expect(details).toContainText('What happened: Recorded review findings are available below.')
  await expect(details).toContainText('Actionable safe findings')
  await expect(details).toContainText('src/example.ts:7 - synthetic rejection')
  await page.getByTestId('rf__edge-trigger').dispatchEvent('click')
  await expect(details).toContainText('Recorded correction trigger')
  await details.getByText('Technical references and retained history').click()
  await expect(details).toContainText('Endpoints: review_one → fix_one')
  await expect(details).toContainText(`Full-range qualification: accepted_full_range.`)
  await page.locator('.react-flow__node[data-id="planned_review"]').click()
  await expect(details).toContainText('Planned review definition — not an agent call.')
  await page.locator('.react-flow__node[data-id="task_a"]').click()
  await expect(details).toContainText(longHostileLabel)
  await expect(details.locator('img')).toHaveCount(0)
  await page.locator('.react-flow__node[data-id="task_b"]').click()
  await expect(details).toContainText('What happened: Repeated generic branch.')
  await expect(details).toContainText('Current blocker: not recorded.')

  const initialNodeHeight = await page.locator('.react-flow__node[data-id="task_b"]').evaluate(element => Number.parseFloat((element as HTMLElement).style.height))
  const stablePositions = Object.fromEntries(overviewGeometry.filter(item => item.id.startsWith('group:') || tasks.some(task => task.ref === item.id)).map(item => [item.id, item.cssBounds]))
  await page.request.get('/fixture-stage?value=overlay')
  await page.clock.fastForward(61_000)
  await expect(page.getByTestId('rf__edge-eligible_secondary_overlay')).toHaveCount(1)
  const overlayGeometry = await readGeometry()
  for (const item of overlayGeometry.filter(item => stablePositions[item.id])) expect(item.cssBounds, `${item.id} is unchanged by a secondary overlay`).toEqual(stablePositions[item.id])

  const initialViewport = await page.locator('.react-flow__viewport').getAttribute('style')
  await page.getByTitle('Zoom In').click()
  const pane = page.locator('.react-flow__pane')
  const paneBox = await pane.boundingBox()
  if (!paneBox) throw new Error('Graph pane is missing')
  await page.mouse.move(paneBox.x + 300, paneBox.y + 220)
  await page.mouse.down()
  await page.mouse.move(paneBox.x + 340, paneBox.y + 250)
  await page.mouse.up()
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())))
  await expect(page.locator('.react-flow__viewport')).not.toHaveAttribute('style', initialViewport ?? '')
  const beforeViewport = await page.locator('.react-flow__viewport').getAttribute('style')
  await page.request.get('/fixture-stage?value=content')
  await page.clock.fastForward(61_000)
  await expect(page.getByTestId('rf__edge-eligible_secondary_overlay')).toHaveCount(0)
  await expect(page.locator('.react-flow__node[data-id="task_b"]')).toContainText(refreshedTaskTitle)
  await expect(page.locator('.react-flow__node[data-id="task_b"]')).toContainText(refreshedBlocker)
  await expect(page.locator('.react-flow__node[data-id="review_two"]')).toContainText('rejected — 2 findings')
  await expect(details).toContainText(refreshedBlocker)
  await expect.poll(() => page.locator('.react-flow__node[data-id="task_b"]').evaluate(element => Number.parseFloat((element as HTMLElement).style.height))).toBeGreaterThan(initialNodeHeight)
  await expect(page.locator('.react-flow__viewport')).toHaveAttribute('style', beforeViewport ?? '')
  await expect(page.locator('.react-flow__node[data-id="task_b"]')).toHaveClass(/selected/)
  await page.waitForTimeout(100)
  await page.clock.fastForward(61_000)
  await assertMeasuredLayout()
  const zoomed = testInfo.outputPath('readable-chain-zoom.png')
  await page.screenshot({ path: zoomed })
  console.log(`Inspection chain screenshot: ${zoomed}`)
  await page.getByText('Loaded history and technical references').click()
  await expect(page.getByText(/unsupported unsupported_observation; legacy_unknown/)).toBeVisible()
})
