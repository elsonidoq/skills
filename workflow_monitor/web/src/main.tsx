import { StrictMode, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import { Background, Controls, ReactFlow, type Edge, type Node, type Viewport, type ReactFlowInstance } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './style.css'
import { graphFor, action, status, outcomeText, recordText, qualificationText, taskNumber, taskTitle, type Observation, type Occurrence, type Followup, type PlannedTask, type ReviewDefinition, type GraphEdge, type ChainExecution } from './graph'
import { layoutNodes } from './layout'

type Acceptance = { state: string; base: string | null; head: string | null }
type AcceptanceItem = { occurrence_ref: string; state: string; ordinal?: number | null; exit_code?: number | null; baseline?: string | null; head?: string | null; no_change?: boolean | null; approved?: boolean | null; finding_count?: number | null; base?: string | null }
type AcceptanceSummary = { checks: AcceptanceItem[]; checkpoints: AcceptanceItem[]; reviews: AcceptanceItem[]; full_range: Acceptance }
type RunnerState = { state: 'live' | 'stopped' | 'unknown'; reason: string | null }
type Run = { ref: string; display_id: string; label: string; started_at: number | null; completeness: string; plan_availability?: string; runner_state?: RunnerState; review_acceptance?: Acceptance; acceptance_summary?: AcceptanceSummary }
type Unknown = { ref: string; run_ref: string; source_seq: number | null; code: string }
type Inventory = { phase_count: number; occurrence_count: number; observation_count: number; total_count: number; loaded_count: number; hidden_count: number; unsupported_count: number }
type Freshness = { read_at: number; last_success_at: number | null; last_recorded_at: number | null; read_state: 'current' | 'unavailable'; warnings: string[] }
type MetricField = { value: number | boolean | null; availability: 'known' | 'unknown'; unknown_reason?: string | null; provenance?: string | null }
type Metrics = { availability: 'complete' | 'partial' | 'unavailable'; reasons: string[]; outcome?: string; role?: string; task_id?: string | null; fixing_round?: number | null; review_ordinal?: number | null; tokens?: Record<string, MetricField>; total_tokens?: MetricField; estimated_usd?: MetricField; selected_session?: { mode: string; reason: string | null }; actual_session?: { mode: string; identity: string | null }; scope?: { kind: string; invocation_id: string | null; session_id: string | null; branch: string | null; epoch: string | null }; before?: SessionSnapshot; after?: SessionSnapshot; compactions?: { count: MetricField; entry_ids: string[]; unknown_reason: string | null }; summary_overhead?: { scope: string; included_in_sdk_deltas: boolean | null; warning: string; unknown_reason: string | null; entries: Array<{ entry_id: string | null; unknown_reason: string | null; usage: Record<string, MetricField | Record<string, MetricField>> }> } }
type SessionSnapshot = { availability: string; scope: string; counters: Record<string, MetricField>; estimated_usd: MetricField; context: Record<string, MetricField>; compaction_entry_ids: string[] }
type Aggregate = { interval_count: number; dispatch_count: number; distinct_membership_count: number; fields: Record<string, { known_subtotal: number | null; full_total: number | null; known_interval_count: number }> }
type FixingRound = { ref: string; run_ref: string; fixing_round: number | null; outcome: string; attempts: Array<{ outcome: string; uncertain: boolean }> }
type Snapshot = { metric_aggregates?: Record<string, { worker_fixer: Aggregate; reviewer: Aggregate }>; metric_artifacts?: Record<string, { status: string; path: string | null; sha: string | null }>; runs: Run[]; phases: Array<{ ref: string; run_ref: string; label: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; unknown_records: Unknown[]; edges: GraphEdge[]; chain?: ChainExecution[]; fixing_rounds?: FixingRound[]; activities?: import('./graph').Activity[]; chain_acceptance?: Record<string, { state: string; terminal_execution_ref: string | null; range: { base: string | null; head: string | null } }>; inventory: Inventory; snapshot_ref: string; next_cursor: string | null; observation?: Freshness }
const POLL_INTERVAL_MS = 60_000
const headers = { 'X-Workflow-Monitor': '1' }
const routeFor = (displayId: string) => `/runs/id-${encodeURIComponent(displayId)}`
function routeDisplayId(): string | null | undefined {
  if (window.location.pathname === '/') return null
  const prefix = '/runs/id-'
  if (!window.location.pathname.startsWith(prefix)) return undefined
  const encoded = window.location.pathname.slice(prefix.length)
  if (!encoded || encoded.includes('/')) return undefined
  try { return decodeURIComponent(encoded) } catch { return undefined }
}
function ordered(runs: Run[]) {
  return [...runs].sort((left, right) => {
    const leftTime = typeof left.started_at === 'number' && Number.isFinite(left.started_at) ? left.started_at : null
    const rightTime = typeof right.started_at === 'number' && Number.isFinite(right.started_at) ? right.started_at : null
    if (leftTime !== null && rightTime !== null && leftTime !== rightTime) return rightTime - leftTime
    if (leftTime !== null && rightTime === null) return -1
    if (leftTime === null && rightTime !== null) return 1
    return left.display_id < right.display_id ? -1 : left.display_id > right.display_id ? 1 : 0
  })
}
async function getJson<T>(path: string): Promise<T> { const response = await fetch(path, { headers }); if (!response.ok) throw new Error(response.status === 409 ? 'The snapshot changed; refreshing history.' : 'The monitor snapshot is unavailable.'); return response.json() as Promise<T> }
const metricLabels: Record<string, string> = { input: 'Input tokens', output: 'Output tokens', cache_read: 'Cached input tokens', cache_write: 'Cached output tokens', total_tokens: 'Total tokens', estimated_usd: 'Cost', total: 'Total tokens', cacheRead: 'Cached input tokens', cacheWrite: 'Cached output tokens', totalTokens: 'Total tokens', cacheWrite1h: 'Cached output tokens (one hour)', reasoning: 'Reasoning tokens', context_window: 'Context window', effective_reserve: 'Reserved context', occupancy: 'Context in use', effective_headroom: 'Available context', compaction_enabled: 'Compaction enabled', compaction_applicable: 'Compaction applicable' }
const ordinary = (name: string) => metricLabels[name] ?? 'Recorded metric'
const plainText = (value: string | null | undefined) => ({ passed: 'Passed', returned: 'Returned', completed: 'Completed', live: 'Live', stopped: 'Stopped', current: 'Current', unavailable: 'Unavailable', abandoned: 'Abandoned', not_started_run_stopped: 'Not started; run stopped', prerequisite_incomplete: 'A prerequisite is incomplete', checkpoint_missing: 'Checkpoint not recorded', incomplete_task_history: 'Incomplete task history', outstanding_input: 'Outstanding input', checkpoint_completed: 'Checkpoint completed', identity_unavailable: 'Identity unavailable', incomplete_history: 'Incomplete history', read_unavailable: 'Read unavailable', missing_end: 'Missing interval end', accepted_full_range: 'Full-range acceptance recorded', correction_only: 'Correction-only review', waiting_for_input: 'Waiting for input', task_started: 'Task started', prerequisite_failed: 'A prerequisite did not complete', completion_unrecorded: 'Completion not recorded', recorded_running: 'Recorded running', returned_without_completion: 'Returned without recorded completion', success: 'Returned successfully', failure: 'Failed', waiting: 'Waiting for input', running: 'Running', pending: 'Pending', blocked: 'Blocked', unknown: 'Unknown', approved: 'Approved', rejected: 'Changes requested', dispatched: 'Dispatched', interrupted: 'Interrupted', failed: 'Failed' }[value ?? ''] ?? (value ? qualificationText(value) : 'Not recorded'))
const availabilityText = (field: MetricField | undefined) => field?.availability === 'known' ? String(field.value) : 'Unavailable from the recorded evidence'
const coverageText = (availability: Metrics['availability']) => ({ complete: 'Complete recorded coverage', partial: 'Partial recorded coverage', unavailable: 'Recorded coverage unavailable' })[availability]
const openingText = (mode: string | undefined) => ({ fresh: 'New session', reused_from_earlier_task: 'Session reused from an earlier task', continued_same_task: 'Session continued for this task', unknown: 'Opening not recorded' })[mode ?? 'unknown'] ?? 'Opening not recorded'
function MetricFieldLine({ label, field }: { label: string; field: MetricField | undefined }) { return <li>{label}: {availabilityText(field)}</li> }
function SessionMetrics({ label, snapshot }: { label: string; snapshot: SessionSnapshot | undefined }) {
  if (!snapshot) return <section><h5>{label} session total</h5><p>Unavailable from the recorded evidence.</p></section>
  return <section><h5>{label} session total</h5><p>This is session context, not call, task, or run spend.</p><ul>{Object.entries(snapshot.counters).map(([name, field]) => <MetricFieldLine key={name} label={ordinary(name)} field={field} />)}<MetricFieldLine label="Cost" field={snapshot.estimated_usd} />{Object.entries(snapshot.context).map(([name, field]) => <MetricFieldLine key={name} label={ordinary(name)} field={field} />)}</ul></section>
}
function AggregateDetails({ label, value }: { label: string; value: Aggregate | undefined }) {
  return <section><h4>{label}</h4>{value ? <><p>{value.interval_count} recorded call{value.interval_count === 1 ? '' : 's'}; {value.dispatch_count} dispatched call{value.dispatch_count === 1 ? '' : 's'}; {value.distinct_membership_count} task membership{value.distinct_membership_count === 1 ? '' : 's'}.</p><ul>{Object.entries(value.fields).map(([name, field]) => <li key={name}>{ordinary(name)}: known subtotal {field.known_subtotal ?? 'Unavailable'}; complete total {field.full_total ?? 'Unavailable'}; {field.known_interval_count} recorded call{field.known_interval_count === 1 ? '' : 's'}.</li>)}</ul></> : <p>Unavailable: recorded calls cannot be attributed exactly.</p>}</section>
}
function MetricDetails({ metrics }: { metrics: Metrics | undefined }) {
  if (!metrics) return <section><h4>This call</h4><p>Metrics unavailable: no recorded metric evidence.</p></section>
  const overhead = metrics.summary_overhead
  return <section className="metric-details"><h4>This call</h4><p>{coverageText(metrics.availability)}. {metrics.reasons.length ? 'Some recorded intervals or dispatches are incomplete.' : 'No recorded coverage warning.'}</p><p>Role: {metrics.role === 'fixing_worker' ? 'Corrective worker' : metrics.role === 'reviewer' ? 'Reviewer' : metrics.role === 'worker' ? 'Worker' : 'Not recorded'}; outcome: {metrics.outcome === 'settled' ? 'Recorded' : 'Not recorded'}.</p><p>Selected opening: {openingText(metrics.selected_session?.mode)}. Confirmed opening: {openingText(metrics.actual_session?.mode)}.</p><p>This call is separate from Task total, Overall run, and session context.</p><ul>{Object.entries(metrics.tokens ?? {}).map(([name, field]) => <MetricFieldLine key={name} label={ordinary(name)} field={field} />)}<MetricFieldLine label="Total tokens" field={metrics.total_tokens} /><MetricFieldLine label="Cost" field={metrics.estimated_usd} /></ul><p>Compactions during this call: {availabilityText(metrics.compactions?.count)}.</p><SessionMetrics label="Before" snapshot={metrics.before} /><SessionMetrics label="After" snapshot={metrics.after} />{overhead && <section><h5>Compaction summary context</h5><p>This summary is already included in This call and is not added again.</p>{overhead.entries.length ? overhead.entries.map((entry, index) => <section key={entry.entry_id ?? index}><p>Recorded summary {index + 1}{entry.unknown_reason ? ': some values unavailable' : ''}</p><ul>{Object.entries(entry.usage).flatMap(([name, value]) => typeof value === 'object' && value !== null && 'availability' in value ? [<MetricFieldLine key={name} label={ordinary(name)} field={value as MetricField} />] : Object.entries(value as Record<string, MetricField>).map(([cost, field]) => <MetricFieldLine key={`${name}-${cost}`} label={name === 'cost' ? 'Cost' : ordinary(`${name}_${cost}`)} field={field} />))}</ul></section>) : <p>No summary context recorded.</p>}</section>}</section>
}
function mergePage(current: Snapshot | null, page: Snapshot): Snapshot {
  // Full work text exists only when retained by the supported recording contract.
  page = { ...page, tasks: page.tasks.map(task => ({ ...task, work_description: typeof task.work_description === 'string' ? task.work_description : null })) }
  if (!current || current.snapshot_ref !== page.snapshot_ref) return page
  const records = [...current.records, ...page.records.filter(item => !current.records.some(old => old.ref === item.ref))]
  const oldUnknown = current.unknown_records ?? []; const pageUnknown = page.unknown_records ?? []
  const unknown_records = [...oldUnknown, ...pageUnknown.filter(item => !oldUnknown.some(old => old.ref === item.ref))]
  return { ...page, next_cursor: current.next_cursor, records, unknown_records, inventory: { ...page.inventory, loaded_count: records.length + unknown_records.length, hidden_count: Math.max(0, page.inventory.total_count - records.length - unknown_records.length) } }
}
function App() {
  const [runs, setRuns] = useState<Run[]>([]); const [selectedRun, setSelectedRun] = useState<string | null>(null); const [filter, setFilter] = useState(''); const [snapshot, setSnapshot] = useState<Snapshot | null>(null); const [lineage, setLineage] = useState<Snapshot[]>([]); const [relations, setRelations] = useState<Followup[]>([]); const [nodes, setNodes] = useState<Node[]>([]); const [edges, setEdges] = useState<Edge[]>([]); const [selected, setSelected] = useState<{ kind: 'node' | 'edge'; id: string } | null>(null); const [viewport, setViewport] = useState<Viewport>({ x: 0, y: 0, zoom: 1 }); const [message, setMessage] = useState('Loading monitor…')
  const flow = useRef<ReactFlowInstance | null>(null); const fitPending = useRef(false); const initialFitComplete = useRef(false);
  const fetchGeneration = useRef(0); const layoutGeneration = useRef(0); const topology = useRef<string | null>(null); const positions = useRef<Record<string, { x: number; y: number }>>({}); const layoutStructure = useRef<string | null>(null); const measurementContent = useRef<string | null>(null); const measurePending = useRef(false); const measurements = useRef<Record<string, { width: number; height: number }>>({}); const runsRef = useRef<Run[]>([]); const [measurementGeneration, setMeasurementGeneration] = useState(0)
  const clearRun = () => { ++fetchGeneration.current; ++layoutGeneration.current; topology.current = null; positions.current = {}; initialFitComplete.current = false; setSnapshot(null); setLineage([]); setRelations([]); setNodes([]); setEdges([]); setSelected(null) }
  const applyLocation = (available: Run[]) => {
    let displayId = routeDisplayId()
    if (displayId === undefined) { clearRun(); setSelectedRun(null); setMessage('The run URL is invalid.'); return }
    if (displayId === null && available.length) { displayId = available[0].display_id; window.history.replaceState(null, '', routeFor(displayId)) }
    if (displayId === null) { clearRun(); setSelectedRun(null); setMessage('No recorded runs are available.'); return }
    const run = available.find(candidate => candidate.display_id === displayId)
    if (!run) { clearRun(); setSelectedRun(null); setMessage(`Run ${displayId} is unavailable.`); return }
    setSelectedRun(current => { if (current !== run.ref) clearRun(); return run.ref })
  }
  useEffect(() => { let active = true; const loadRuns = async () => { try { const data = await getJson<{ runs: Run[] }>('/api/monitor/v1/runs'); if (!active) return; const sorted = ordered(data.runs); runsRef.current = sorted; setRuns(sorted); applyLocation(sorted) } catch (error) { if (active) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') } }; void loadRuns(); const timer = window.setInterval(() => void loadRuns(), POLL_INTERVAL_MS); return () => { active = false; window.clearInterval(timer) } }, [])
  useEffect(() => { const onPopState = () => applyLocation(runsRef.current); window.addEventListener('popstate', onPopState); return () => window.removeEventListener('popstate', onPopState) }, [])
  useEffect(() => { if (!selectedRun) return; const generation = ++fetchGeneration.current; let active = true; const loadSnapshot = async () => { try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/snapshot`); let followups: Followup[] = []; try { let cursor: string | null = null; do { const result: { followups: Followup[]; next_cursor?: string | null } = await getJson(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/followups?snapshot=${encodeURIComponent(page.snapshot_ref)}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ''}`); followups.push(...result.followups); cursor = result.next_cursor ?? null } while (cursor) } catch { /* A snapshot remains usable when a prior closed fixture has no followup route. */ } const linkedRefs = [...new Set(followups.flatMap(item => [item.run_ref, item.source_run_ref]).filter(ref => ref !== selectedRun))]; const linked = (await Promise.all(linkedRefs.map(async ref => { try { return await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(ref)}/snapshot`) } catch { return null } }))).filter((item): item is Snapshot => item !== null); if (active && generation === fetchGeneration.current) { setSnapshot(current => mergePage(current, page)); setRelations(followups); setLineage(current => linked.map(item => mergePage(current.find(old => old.snapshot_ref === item.snapshot_ref) ?? null, item))); setMessage('Updated from the recorded snapshot.') } } catch (error) { if (active && generation === fetchGeneration.current) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') } }; void loadSnapshot(); const timer = window.setInterval(() => void loadSnapshot(), POLL_INTERVAL_MS); return () => { active = false; window.clearInterval(timer); ++fetchGeneration.current } }, [selectedRun])
  const loadMore = async () => { if (!snapshot || !selectedRun || !snapshot.next_cursor) return; const generation = fetchGeneration.current; try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/history?snapshot=${encodeURIComponent(snapshot.snapshot_ref)}&cursor=${encodeURIComponent(snapshot.next_cursor)}`); if (generation === fetchGeneration.current) setSnapshot(current => ({ ...mergePage(current, page), next_cursor: page.next_cursor })) } catch (error) { if (generation !== fetchGeneration.current) return; setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.'); try { const fresh = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/snapshot`); if (generation === fetchGeneration.current) setSnapshot(fresh) } catch { /* Keep the last safe view on read failure. */ } } }
  const loadLinkedMore = async (linked: Snapshot) => {
    const ref = linked.occurrences[0]?.run_ref ?? linked.records[0]?.run_ref ?? linked.unknown_records[0]?.run_ref
    if (!ref || !linked.next_cursor) return
    const generation = fetchGeneration.current
    try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(ref)}/history?snapshot=${encodeURIComponent(linked.snapshot_ref)}&cursor=${encodeURIComponent(linked.next_cursor)}`); if (generation === fetchGeneration.current) setLineage(current => current.map(item => item.snapshot_ref === linked.snapshot_ref ? { ...mergePage(item, page), next_cursor: page.next_cursor } : item)) } catch (error) { if (generation === fetchGeneration.current) setMessage(error instanceof Error ? error.message : 'History unavailable.') }
  }
  useEffect(() => {
    if (!snapshot || !selectedRun) return
    const graph = graphFor(snapshot, lineage, relations)
    const known = new Set([...graph.nodes.map(node => node.id), ...graph.edges.map(edge => edge.id)])
    setSelected(current => current && known.has(current.id) ? current : null)
    setEdges(graph.edges)
    const contentKey = JSON.stringify(graph.nodes.map(node => [node.id, node.data.label, node.data.status]))
    const contentChanged = measurementContent.current !== contentKey
    measurementContent.current = contentKey
    const layoutKey = JSON.stringify({ topology: graph.topology, sizes: graph.nodes.map(node => [node.id, measurements.current[node.id] ?? { width: 180, height: 70 }]) })
    const refreshNodes = () => setNodes(current => current.map(node => {
      const fresh = graph.nodes.find(item => item.id === node.id)
      return fresh ? { ...node, data: fresh.data, className: fresh.className } : node
    }))
    if (topology.current === layoutKey) {
      measurePending.current = contentChanged
      refreshNodes()
      return
    }
    const structureChanged = layoutStructure.current !== graph.topology
    if (structureChanged) fitPending.current = true
    measurePending.current = true
    const generation = ++layoutGeneration.current
    let active = true
    void layoutNodes(
      graph.nodes.map(node => ({ id: node.id, size: measurements.current[node.id] ?? { width: 180, height: 70 } })),
      graph.edges.map(edge => ({ source: edge.source, target: edge.target }))
    ).then(layout => {
      if (!active || generation !== layoutGeneration.current) return
      topology.current = layoutKey
      layoutStructure.current = graph.topology
      const byId = new Map(layout.nodes.map(node => [node.id, node]))
      setNodes(graph.nodes.map(node => {
        const layoutNode = byId.get(node.id)!
        const position = positions.current[node.id] ?? { x: layoutNode.x, y: layoutNode.y }
        return { ...node, position, style: { width: layoutNode.width, height: layoutNode.height } }
      }))
    })
    return () => { active = false }
  }, [selectedRun, snapshot, lineage, relations, measurementGeneration])
  useEffect(() => {
    if (!nodes.length || !measurePending.current) return
    const frame = requestAnimationFrame(() => {
      if (!measurePending.current) return
      measurePending.current = false
      const next = { ...measurements.current }
      let changed = false
      document.querySelectorAll<HTMLElement>('.react-flow__node[data-id]').forEach(element => {
        const id = element.dataset.id
        if (!id) return
        const horizontalBorder = element.offsetWidth - element.clientWidth
        const verticalBorder = element.offsetHeight - element.clientHeight
        const retainedHeight = element.style.height
        element.style.height = 'auto'
        const size = {
          width: Math.ceil(Math.max(element.offsetWidth, element.scrollWidth + horizontalBorder)),
          height: Math.ceil(Math.max(element.offsetHeight, element.scrollHeight + verticalBorder))
        }
        element.style.height = retainedHeight
        const previous = next[id]
        if (size.width && size.height && (previous?.width !== size.width || previous.height !== size.height)) { next[id] = size; changed = true }
      })
      if (!initialFitComplete.current) fitPending.current = true
      if (changed) { measurements.current = next; topology.current = null; setMeasurementGeneration(current => current + 1) }
    })
    return () => cancelAnimationFrame(frame)
  }, [nodes])
  useEffect(() => { if (nodes.length && fitPending.current && flow.current) { fitPending.current = false; initialFitComplete.current = true; void flow.current.fitView({ padding: .12, maxZoom: 1 }) } }, [nodes])
  const details = useMemo(() => {
    if (!snapshot || !selected) return null
    const all = [snapshot, ...lineage]
    const runFor = (ref: string) => all.flatMap(item => item.runs).find(run => run.ref === ref)
    const acceptanceDetails = (run: Run | undefined) => {
      const summary = run?.acceptance_summary
      if (!summary) return <section><h4>Acceptance</h4><p>Acceptance summary not recorded.</p></section>
      const full = summary.full_range
      return <section><h4>Acceptance</h4><p>Full-range qualification: {plainText(full?.state)}.</p><details><summary>Acceptance history</summary>{summary.checks.map((item, index) => <p key={`check-${index}`}>Check {index + 1}: {plainText(item.state)}; exit {item.exit_code ?? 'unknown'}.</p>)}{summary.checkpoints.map((item, index) => <p key={`checkpoint-${index}`}>Checkpoint {index + 1}: {plainText(item.state)}; {item.no_change == null ? 'change status unknown' : item.no_change ? 'no changes' : 'changes recorded'}.</p>)}{summary.reviews.map((item, index) => <p key={`review-${index}`}>Review {index + 1}: {plainText(item.state)}; {item.approved == null ? 'decision unknown' : item.approved ? 'approved' : 'changes requested'}; findings {item.finding_count ?? 'unknown'}.</p>)}</details></section>
    }
    const metricContext = (runRef: string, taskMetrics?: unknown) => {
      const data = all.find(item => item.metric_aggregates?.[runRef] || item.metric_artifacts?.[runRef])
      const aggregates = data?.metric_aggregates?.[runRef]
      const artifact = data?.metric_artifacts?.[runRef]
      return <>{taskMetrics !== undefined && <AggregateDetails label="Task total" value={taskMetrics as Aggregate | undefined} />}<AggregateDetails label="Overall run — workers and corrective workers" value={aggregates?.worker_fixer} /><AggregateDetails label="Overall run — reviewers (not task spend)" value={aggregates?.reviewer} /><section><h4>Metric evidence</h4><p>{artifact?.status === 'committed' ? 'Recorded metric evidence is available.' : artifact?.status === 'failed' ? 'Recorded metric evidence is incomplete or unavailable.' : 'Metric evidence status is not recorded.'}</p><p>This evidence is separate from the reviewed code range and does not change execution or review outcome.</p></section></>
    }
    const history = (children: ReactNode) => <details><summary>Recorded history</summary>{children}</details>
    if (selected.kind === 'edge') {
      const edge = edges.find(item => item.id === selected.id)
      const graph = graphFor(snapshot, lineage, relations)
      const endpoint = (ref: string) => graph.nodes.find(node => node.id === ref)
      const endpointLabel = (ref: string) => String(endpoint(ref)?.data.label ?? 'Unknown recorded activity')
      const edgeRun = edge ? (endpoint(edge.source)?.data.identity as { runRef?: string } | undefined)?.runRef : undefined
      const data = edge?.data as { relation?: string; relations?: string[]; resolution?: string; qualification?: string; identity?: Record<string, unknown>; identities?: Record<string, unknown>[] } | undefined
      const facts = data?.relations?.length ? data.relations : [data?.relation ?? 'unknown']
      const relationLabel = (relation: string) => ({ 'recorded-input': 'Recorded input', 'recorded-correction': 'Recorded correction', 'recorded-review-input': 'Recorded review input', 'recorded-correction-trigger': 'Recorded correction trigger', 'recorded-correction-predecessor': 'Recorded correction predecessor', 'declared-prerequisite': 'Declared prerequisite', 'recorded-stop-support': 'Recorded stopping support', chain_trigger: 'Recorded correction trigger', chain_predecessor: 'Recorded correction predecessor', chain_check: 'Recorded correction check', chain_checkpoint: 'Recorded correction checkpoint', 'declared-cross-run-correction': 'Declared cross-run correction' } as Record<string, string>)[relation] ?? 'Unknown recorded relation'
      return edge ? <><h3>{facts.length > 1 ? 'Recorded relationships' : relationLabel(facts[0])}</h3><p>{endpointLabel(edge.source)} → {endpointLabel(edge.target)}</p><ul>{facts.map((fact, index) => <li key={`${fact}-${index}`}>{relationLabel(fact)}</li>)}</ul><p>{data?.qualification ?? (data?.resolution ? `Qualification: ${data.resolution}.` : 'Qualification not recorded.')}</p>{acceptanceDetails(edgeRun ? runFor(edgeRun) : undefined)}</> : null
    }
    const graph = graphFor(snapshot, lineage, relations)
    const graphNode = graph.nodes.find(node => node.id === selected.id)
    const identity = graphNode?.data.identity as { invocationId?: string | null; executionId?: string | null } | undefined
    const task = all.flatMap(item => item.tasks).find(item => item.ref === selected.id || `planned-task:${item.run_ref}:${item.ref}` === selected.id)
    if (task) { const runTasks = all.flatMap(item => item.tasks); const recorded = identity?.invocationId ? all.flatMap(item => item.activities ?? []).find(activity => activity.run_ref === task.run_ref && activity.invocation_id === identity.invocationId) : undefined; return <><h3>{taskNumber(task, runTasks)} — {taskTitle(task)}</h3><p>Role: planned worker.</p><p>State: {String(graphNode?.data.status ?? 'Unknown')}.</p><p>Full retained work text: {task.work_description ?? 'Unknown: this supported recording did not retain full work text.'}</p><p>Current blocker: {task.annotation?.label ?? plainText(task.annotation?.code ?? task.reason?.code)}.</p><p>Prerequisites: {task.prerequisite_refs.length ? `${task.prerequisite_refs.length} recorded task${task.prerequisite_refs.length === 1 ? '' : 's'}` : 'none'}.</p><MetricDetails metrics={recorded?.metrics as Metrics | undefined} />{recorded && metricContext(task.run_ref, recorded.task_metrics)}{acceptanceDetails(runFor(task.run_ref))}</> }
    const definition = all.flatMap(item => item.review_definitions ?? []).find(item => item.ref === selected.id || `planned-review:${item.run_ref}:${item.ref}` === selected.id)
    if (definition) { const execution = identity?.executionId ? all.flatMap(item => item.chain ?? []).find(item => item.run_ref === definition.run_ref && item.execution_id === identity.executionId) : undefined; const recorded = execution ? all.flatMap(item => item.activities ?? []).find(activity => activity.run_ref === definition.run_ref && activity.role === 'reviewer' && activity.invocation_id === execution.execution_id) : undefined; return <><h3>Planned independent review</h3><p>Role: reviewer. State: {String(graphNode?.data.status ?? 'planned — not started')}.</p><p>Verdict: {execution ? plainText(execution.outcome) : 'Not recorded'}.</p>{execution?.findings.length ? <section><h4>Actionable safe findings</h4>{execution.findings.map((finding, index) => <p key={index}>{finding}</p>)}</section> : <p>Actionable safe findings: not recorded.</p>}<MetricDetails metrics={recorded?.metrics as Metrics | undefined} />{recorded && metricContext(definition.run_ref, recorded.task_metrics)}{acceptanceDetails(runFor(definition.run_ref))}</> }
    const chain = all.flatMap(item => item.chain ?? []).find(item => item.ref === selected.id)
    if (chain) {
      const chainActivities = all.flatMap(item => item.activities ?? []).filter(activity => activity.run_ref === chain.run_ref && activity.occurrence_ref !== null && chain.occurrence_refs.includes(activity.occurrence_ref))
      return <><h3>{chain.role === 'fixer' ? `Scheduled fixing round ${chain.fixing_round ?? 'unknown'}` : chain.role === 'reviewer' ? `Review ${chain.review_ordinal ?? 'unknown'}` : 'Recorded execution'}</h3><p>Role: {chain.role === 'reviewer' ? 'independent reviewer' : 'fixing worker'}.</p><p>Execution: {String(graphNode?.data.status ?? 'Unknown')}.</p><p>Verdict: {plainText(chain.outcome)}.</p><p>What happened: {chain.findings.length ? 'Recorded review findings are available below.' : chain.role === 'fixer' ? 'A fixing round was scheduled; individual calls are not inferred.' : 'not recorded'}.</p><p>Current blocker: {chain.outcome === 'rejected' ? 'Review requested changes.' : 'not recorded'}.</p>{chain.findings.length ? <section><h4>Actionable safe findings</h4>{chain.findings.map((finding, index) => <p key={index}>{finding}</p>)}</section> : <p>Actionable safe findings: not recorded.</p>}{history(<>{chain.occurrence_refs.length ? <p>{chain.occurrence_refs.length} recorded workflow events support this result.</p> : <p>No supporting workflow events were retained.</p>}{chain.attempts?.map((attempt, index) => <p key={index}>Attempt {index + 1}: {plainText(attempt.outcome)}{attempt.uncertain ? '; recorded evidence is incomplete' : ''}.</p>)}</>)}{chainActivities.length ? <section><h4>Recorded invocation metrics</h4>{chainActivities.map(activity => <MetricDetails key={activity.ref} metrics={activity.metrics as Metrics | undefined} />)}</section> : <MetricDetails metrics={undefined} />}{metricContext(chain.run_ref)}{acceptanceDetails(runFor(chain.run_ref))}</> }
    const activity = all.flatMap(item => item.activities ?? []).find(item => item.ref === selected.id)
    if (activity) {
      const task = activity.task_ref ? all.flatMap(item => item.tasks).find(item => item.ref === activity.task_ref && item.run_ref === activity.run_ref) : undefined
      const title = `${activity.role === 'fixing_worker' ? 'Corrective worker' : activity.role === 'reviewer' ? 'Reviewer' : activity.role === 'worker' ? 'Worker' : 'Recorded activity'}${task ? ` — ${taskTitle(task)}` : ''}${activity.invocation_kind === 'corrective_worker' ? ' (correction)' : ''}`
      const own = all.flatMap(item => item.records).filter(record => activity.record_refs.includes(record.ref) && record.run_ref === activity.run_ref)
      const rendered = graphFor(snapshot, lineage, relations).nodes.find(node => node.id === activity.ref)
      const qualification = rendered?.data.relationQualification
      return <><h3>{title}</h3>{task && <><p>{taskNumber(task, all.flatMap(item => item.tasks))} — {taskTitle(task)}.</p><p>Full retained work text: {task.work_description ?? 'Unknown: this supported recording did not retain full work text.'}</p></>}<p>Role: {activity.role === 'fixing_worker' ? 'corrective worker' : activity.role === 'reviewer' ? 'reviewer' : activity.role === 'worker' ? 'worker' : 'not recorded'}.</p><p>Execution: {String(graphNode?.data.status ?? 'Unknown')}.</p><p>What happened: {activity.error_category ? `Recorded safe error category: ${activity.error_category}.` : 'not recorded'}.</p><p>Stopping reason: {activity.stopped_by_ref ? 'Recorded workflow stopped this activity.' : 'unknown/not recorded'}.</p>{qualification && <p>Relation qualification: {String(qualification)}</p>}{history(<>{own.length ? own.map((record, index) => <p key={record.ref}>Event {index + 1}: {recordText(record)}</p>) : <p>No loaded event history.</p>}</>)}<MetricDetails metrics={activity.metrics as Metrics | undefined} />{metricContext(activity.run_ref, activity.task_metrics)}{acceptanceDetails(runFor(activity.run_ref))}<p>Only loaded observations are shown; use history below for retained evidence.</p></>
    }
    const occurrence = all.flatMap(item => item.occurrences).find(item => item.ref === selected.id)
    if (!occurrence) return null
    const own = all.flatMap(item => item.records).filter(item => item.occurrence_ref === occurrence.ref && item.run_ref === occurrence.run_ref)
    const supporting = all.flatMap(item => item.occurrences).filter(item => item.run_ref === occurrence.run_ref && item.role === 'non_model' && (item.support_ref === occurrence.ref || item.parent_ref === occurrence.ref))
    return <><h3>{action(occurrence, all)}</h3><p>Role: {occurrence.role === 'non_model' ? 'workflow step' : occurrence.role}.</p><p>Outcome: {outcomeText(occurrence, own)}.</p><p>What happened: {own.length ? 'Recorded lifecycle evidence is available below.' : 'not recorded'}.</p><p>Current blocker: {occurrence.stopping ? 'Recorded workflow stopping step.' : 'not recorded'}.</p>{occurrence.execution_summary?.qualification && <p>Recorded execution qualification: {qualificationText(occurrence.execution_summary.qualification)}.</p>}{history(<>{own.map((item, index) => <p key={item.ref}>Event {index + 1}: {recordText(item)}</p>)}{supporting.map((item, index) => <section key={item.ref}><h4>Related event {index + 1}: {action(item, all)}</h4><p>{item.stopping ? 'Workflow stopping step.' : 'Supporting observation.'}</p>{all.flatMap(value => value.records).filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref).map((record, event) => <p key={record.ref}>Event {event + 1}: {recordText(record)}</p>)}</section>)}</>)}{acceptanceDetails(runFor(occurrence.run_ref))}<p>Only loaded observations are shown; use history below for retained evidence.</p></>
  }, [edges, lineage, selected, snapshot])
  // ReactFlow retains measured dimensions/handles by node identity. Recreating nodes
  // on viewport moves hides calls and removes connectors until ResizeObserver reruns.
  const renderedNodes = useMemo(() => nodes.map(node => {
    if (node.id.startsWith('group:')) return node
    const word = String(node.data.status).toLowerCase()
    const stateClass = word.includes('running') ? 'running' : word.includes('waiting') || word.includes('blocked') ? 'waiting' : word.includes('failed') || word.includes('interrupted') ? 'failed' : word.includes('returned') || word.includes('approved') || word.includes('rejected') ? 'success' : word.includes('planned') || word.includes('pending') || word.includes('not started') ? 'pending' : 'neutral'
    return { ...node, className: `${node.className ?? ''} ${stateClass}`, selected: selected?.kind === 'node' && selected.id === node.id, data: { ...node.data, label: <>
      <strong>{String(node.data.label)}</strong>
      <small>{String(node.data.status)}</small>
      </> } }
  }), [nodes, selected])
  const allOccurrences = snapshot ? [snapshot, ...lineage].flatMap(item => item.occurrences) : []; const failures = allOccurrences.filter(item => item.outcome === 'failed').length; const incomplete = allOccurrences.filter(item => item.completeness === 'incomplete').length; const allTasks = [snapshot, ...lineage].flatMap(value => value?.tasks ?? []); const waiting = allTasks.filter(task => task.annotation?.code === 'waiting_for_input').length + allOccurrences.filter(item => !allTasks.some(task => task.ref === item.task_ref) && status(item, [snapshot, ...lineage].flatMap(value => value?.records ?? [])) === 'waiting').length
  const selectedRunInfo = runs.find(run => run.ref === selectedRun); const acceptance = selectedRunInfo?.review_acceptance; const acceptanceText = acceptance?.state === 'accepted_full_range' ? 'Full-range acceptance is recorded.' : acceptance?.state === 'correction_only' ? 'Correction-only review; current work is not accepted.' : 'Current lineage acceptance is unknown.'
  const freshness = snapshot?.observation; const freshnessText = freshness ? `Read ${plainText(freshness.read_state)}; last successful read ${freshness.last_success_at ?? 'unknown'}; last recorded activity ${freshness.last_recorded_at ?? 'unknown'}${freshness.warnings.length ? `; warning: ${freshness.warnings.map(plainText).join(', ')}` : ''}.` : 'Read state unknown.'
  const runnerText = selectedRunInfo?.runner_state ? `Recorded runner ${plainText(selectedRunInfo.runner_state.state)}${selectedRunInfo.runner_state.reason ? ` (${plainText(selectedRunInfo.runner_state.reason)})` : ''}; process presence does not prove progress.` : 'Recorded runner unknown.'
  return <main>
    <aside aria-label="Recorded runs">
    <h1>Workflow monitor</h1>
    <p className="status" role="status">{message}</p>
    <h2>Runs</h2>
    <label className="run-filter">Filter runs <input value={filter} onChange={event => setFilter(event.target.value)} placeholder="Filter runs" /></label>
    <div className="run-list">{runs.filter(run => run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())).map((run, index) => <button key={run.ref} className={run.ref === selectedRun ? 'selected' : ''} onClick={() => { if (run.ref === selectedRun) return; window.history.pushState(null, '', routeFor(run.display_id)); applyLocation(runsRef.current) }}>Run {index + 1} · {run.label} · {run.completeness}</button>)}</div>
    {filter && !runs.some(run => run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())) && <p>No runs match this filter.</p>}
    {filter && selectedRun && !runs.some(run => run.ref === selectedRun && run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())) && <p>The selected run is outside this filter.</p>}
    </aside>
    <section className="viewer">
    <header>
    <h2>Selected run graph</h2>
    <p aria-label="Selected run">Selected run: {selectedRunInfo ? `Run ${runs.findIndex(run => run.ref === selectedRunInfo.ref) + 1} — ${selectedRunInfo.label}` : 'unknown'}</p>
    <p>Pan and zoom the graph. Select a node or edge for its brief details.</p>
    </header>
    <div className="legend" aria-label="Status legend">
    <span className="pending">Grey: planned or pending</span>
    <span className="running">Blue: recorded running</span>
    <span className="success">Green: execution returned (a reviewer may still reject)</span>
    <span className="failed">Red: execution failure / stopping step</span>
    <span className="waiting">Amber: evidence-backed waiting or blocked</span>
    <span className="neutral">Neutral: qualified unknown or incomplete</span>
    <span className="plan">Full-snapshot plan progress is not execution outcome or acceptance</span>
    <span className="acceptance">Acceptance is in Details; skipped/cancelled unsupported</span>
    <span>Relations: declared prerequisites; recorded stops and qualified corrections. Select an edge for details.</span>
    {snapshot && selectedRunInfo?.plan_availability !== 'complete' && <span className="unavailable">Complete graph unavailable</span>}
    </div>
    <div className="execution-view">
    <div className="graph" aria-label="Workflow graph">
    <ReactFlow<Node, Edge> nodes={renderedNodes} edges={edges.map(edge => ({ ...edge, selected: selected?.kind === 'edge' && selected.id === edge.id }))} onInit={instance => { flow.current = instance }} minZoom={.15} viewport={viewport} onMove={(_, next) => setViewport(next)} onNodeDragStop={(_, node) => { positions.current[node.id] = node.position; setNodes(current => current.map(item => item.id === node.id ? { ...item, position: node.position } : item)) }} onNodeClick={(_, node) => setSelected({ kind: 'node', id: node.id })} onEdgeClick={(_, edge) => setSelected({ kind: 'edge', id: edge.id })}>
    <Background />
    <Controls />
    </ReactFlow>
    </div>
    <section className="selection-details" aria-label="Selected execution details" aria-live="polite">
    <h2>Details</h2>{details ?? <p>Select a graph node or edge.</p>}</section>
    </div>
    <section className="details">
    <h2>Recorded evidence</h2>
    <p aria-label="Lineage acceptance">{acceptanceText}</p>
    <p aria-label="Read freshness">{freshnessText}</p>
    <p aria-label="Runner liveness">{runnerText}</p>
    <p>{relations.length ? `${relations.length} declared follow-up relationship${relations.length === 1 ? '' : 's'} recorded.` : 'No declared followups.'}</p>
    <p>{snapshot ? `Inventory: ${snapshot.inventory.total_count ?? snapshot.inventory.observation_count} total, ${snapshot.inventory.loaded_count ?? snapshot.records.length} loaded, ${snapshot.inventory.hidden_count} hidden, ${snapshot.inventory.unsupported_count ?? 0} unsupported.` : 'Inventory unavailable.'}</p>{snapshot && <p>Inventory: {snapshot.inventory.observation_count} records, {snapshot.inventory.occurrence_count} occurrences, {snapshot.inventory.phase_count} phases; {snapshot.inventory.hidden_count} hidden.</p>}<p aria-label="Collapsed history badges">{failures} failed; {waiting} waiting; {incomplete} incomplete.</p>{snapshot && <details>
    <summary>Loaded history</summary>{[snapshot, ...lineage].map((item, section) => <section key={item.snapshot_ref ?? item.runs[0]?.ref}>
    <h3>{section === 0 ? 'Selected run history' : 'Related run history'}</h3>{item.tasks.map(task => <section key={task.ref}><p>{taskNumber(task, item.tasks)} — {taskTitle(task)}; state {plainText(task.progress?.state)}.</p><p>Full retained work text: {task.work_description ?? 'Unknown: this supported recording did not retain full work text.'}</p></section>)}{item.fixing_rounds?.map((round, index) => <section key={round.ref}><p>Scheduled fixing round {round.fixing_round ?? index + 1}: {plainText(round.outcome)}. Individual calls are shown only when separately recorded.</p>{round.attempts.map((attempt, attemptIndex) => <p key={attemptIndex}>Round update {attemptIndex + 1}: {plainText(attempt.outcome)}{attempt.uncertain ? '; evidence is incomplete' : ''}.</p>)}</section>)}{item.chain?.flatMap(execution => execution.attempts?.map((attempt, index) => <p key={`${execution.ref}-${index}`}>Review {execution.review_ordinal ?? 'unknown'} attempt {index + 1}: {plainText(attempt.outcome)}{attempt.uncertain ? '; evidence is incomplete' : ''}.</p>) ?? [])}{item.occurrences.map((occurrence, index) => <p key={occurrence.ref}>Activity {index + 1}: {action(occurrence, [item])}; {outcomeText(occurrence, item.records)}.</p>)}{item.records.map((record, index) => <p key={record.ref}>Event {index + 1}: {recordText(record)}.</p>)}{item.unknown_records?.map((record, index) => <p key={record.ref}>Unavailable record {index + 1}: {plainText(record.code)}.</p>)}</section>)}</details>}{lineage.filter(item => item.next_cursor).map(item => <button key={item.snapshot_ref} onClick={() => void loadLinkedMore(item)}>Load correction history</button>)}{snapshot?.next_cursor && <button onClick={() => void loadMore()}>Load more history</button>}</section>
    </section>
    </main>
}
createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
