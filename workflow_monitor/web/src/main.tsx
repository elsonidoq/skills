import { StrictMode, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import { Background, Controls, ReactFlow, type Edge, type Node, type Viewport, type ReactFlowInstance } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './style.css'
import { graphFor, action, status, outcomeText, recordText, taskTitle, type Observation, type Occurrence, type Followup, type PlannedTask, type ReviewDefinition, type GraphEdge, type ChainExecution } from './graph'
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
type Snapshot = { metric_aggregates?: Record<string, { worker_fixer: Aggregate; reviewer: Aggregate }>; metric_artifacts?: Record<string, { status: string; path: string | null; sha: string | null }>; runs: Run[]; phases: Array<{ ref: string; run_ref: string; label: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; unknown_records: Unknown[]; edges: GraphEdge[]; chain?: ChainExecution[]; activities?: import('./graph').Activity[]; chain_acceptance?: Record<string, { state: string; terminal_execution_ref: string | null; range: { base: string | null; head: string | null } }>; inventory: Inventory; snapshot_ref: string; next_cursor: string | null; observation?: Freshness }
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
function source(runRef: string) { return `source ${runRef}` }
function metricValue(field: MetricField | undefined) { return field?.availability === 'known' ? String(field.value) : `unknown${field?.unknown_reason ? ` (${field.unknown_reason})` : ''}` }
function MetricFieldLine({ label, field }: { label: string; field: MetricField | undefined }) { return <li>{label}: {metricValue(field)}{field?.provenance ? ` [${field.provenance}]` : ''}</li> }
function SessionMetrics({ label, snapshot }: { label: string; snapshot: SessionSnapshot | undefined }) {
  if (!snapshot) return <section><h5>{label} session cumulative</h5><p>Unknown session snapshot.</p></section>
  return <section><h5>{label} session cumulative ({snapshot.availability})</h5><p>Scope: {snapshot.scope}; compaction references: {snapshot.compaction_entry_ids.length ? snapshot.compaction_entry_ids.join(', ') : 'none recorded'}.</p><ul>{Object.entries(snapshot.counters).map(([name, field]) => <MetricFieldLine key={name} label={`${name} tokens`} field={field} />)}<MetricFieldLine label="estimated USD" field={snapshot.estimated_usd} />{Object.entries(snapshot.context).map(([name, field]) => <MetricFieldLine key={name} label={name.replaceAll('_', ' ')} field={field} />)}</ul></section>
}
function AggregateDetails({ label, value }: { label: string; value: Aggregate | undefined }) {
  return <section><h4>{label}</h4>{value ? <><p>Recorded intervals: {value.interval_count}; dispatched calls: {value.dispatch_count}; distinct task memberships: {value.distinct_membership_count}.</p><ul>{Object.entries(value.fields).map(([name, field]) => <li key={name}>{name === 'estimated_usd' ? 'estimated USD' : name === 'total_tokens' ? 'total tokens' : `${name.replaceAll('_', '-')} tokens`}: known subtotal {field.known_subtotal ?? 'unavailable'}; full total {field.full_total ?? 'unavailable'}; known intervals {field.known_interval_count}.</li>)}</ul></> : <p>Unavailable: exact dispatch attribution not recorded.</p>}</section>
}
function MetricDetails({ metrics }: { metrics: Metrics | undefined }) {
  if (!metrics) return <section><h4>Invocation metrics</h4><p>Unavailable: no metric projection recorded.</p></section>
  const overhead = metrics.summary_overhead
  return <section className="metric-details"><h4>Invocation metrics</h4><p>Availability: {metrics.availability}; {metrics.reasons.length ? `coverage reasons: ${metrics.reasons.join(', ')}` : 'coverage reasons: none recorded'}.</p><p>Scope: {metrics.scope?.kind ?? 'unknown'}; invocation {metrics.scope?.invocation_id ?? 'unknown'}; session {metrics.scope?.session_id ?? 'unknown'}; branch {metrics.scope?.branch ?? 'unknown'}; epoch {metrics.scope?.epoch ?? 'unknown'}.</p><p>Invocation role: {metrics.role ?? 'unknown'}; outcome: {metrics.outcome ?? 'unknown'}; task: {metrics.task_id ?? 'not applicable'}; worker/fixer round: {metrics.fixing_round ?? 'not applicable'}; reviewer ordinal: {metrics.review_ordinal ?? 'not applicable'}.</p><p>Selected opening: {metrics.selected_session?.mode ?? 'unknown'}; reason: {metrics.selected_session?.reason ?? 'unknown'}. Confirmed opening: {metrics.actual_session?.mode ?? 'unknown'}; actual identity: {metrics.actual_session?.identity ?? 'unknown'}.</p><p>Selection intent is not a confirmed opening. Invocation usage is not task-wide dispatch totals or reviewer/session spend.</p><ul>{Object.entries(metrics.tokens ?? {}).map(([name, field]) => <MetricFieldLine key={name} label={`${name.replaceAll('_', '-')} tokens`} field={field} />)}<MetricFieldLine label="total tokens" field={metrics.total_tokens} /><MetricFieldLine label="estimated USD" field={metrics.estimated_usd} /></ul><p>Invocation compactions: {metricValue(metrics.compactions?.count)}; references: {metrics.compactions?.entry_ids?.length ? metrics.compactions.entry_ids.join(', ') : 'none recorded'}{metrics.compactions?.unknown_reason ? `; ${metrics.compactions.unknown_reason}` : ''}.</p><SessionMetrics label="Before" snapshot={metrics.before} /><SessionMetrics label="After" snapshot={metrics.after} />{overhead && <section><h5>Compaction summary subset</h5><p>Scope: {overhead.scope}; {overhead.warning}; included in SDK deltas: {overhead.included_in_sdk_deltas === null ? 'unknown' : String(overhead.included_in_sdk_deltas)}{overhead.unknown_reason ? `; ${overhead.unknown_reason}` : ''}. Do not add this subset to invocation totals.</p>{overhead.entries.length ? overhead.entries.map(entry => <section key={entry.entry_id ?? 'unknown'}><p>Summary {entry.entry_id ?? 'unknown'}{entry.unknown_reason ? `: ${entry.unknown_reason}` : ''}</p><ul>{Object.entries(entry.usage).flatMap(([name, value]) => typeof value === 'object' && value !== null && 'availability' in value ? [<MetricFieldLine key={name} label={name} field={value as MetricField} />] : Object.entries(value as Record<string, MetricField>).map(([cost, field]) => <MetricFieldLine key={`${name}-${cost}`} label={`${name} ${cost}`} field={field} />))}</ul></section>) : <p>No summary subset entries recorded.</p>}</section>}</section>
}
function mergePage(current: Snapshot | null, page: Snapshot): Snapshot {
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
      return <section><h4>Acceptance</h4><p>Full-range qualification: {full?.state ?? 'unknown'}.</p><details><summary>Full retained acceptance details</summary><p>{full?.base && full?.head ? `${full.base} → ${full.head}` : 'Range unknown'}</p>{summary.checks.map(item => <p key={`check-${item.occurrence_ref}`}>Check {item.occurrence_ref}: {item.state}; ordinal {item.ordinal ?? 'unknown'}; exit {item.exit_code ?? 'unknown'}</p>)}{summary.checkpoints.map(item => <p key={`checkpoint-${item.occurrence_ref}`}>Checkpoint {item.occurrence_ref}: {item.state}; {item.baseline ?? 'unknown'} → {item.head ?? 'unknown'}; no change {String(item.no_change ?? 'unknown')}</p>)}{summary.reviews.map(item => <p key={`review-${item.occurrence_ref}`}>Review {item.occurrence_ref}: {item.state}; approved {String(item.approved ?? 'unknown')}; findings {item.finding_count ?? 'unknown'}; range {item.base ?? 'unknown'} → {item.head ?? 'unknown'}</p>)}</details></section>
    }
    const metricContext = (runRef: string, taskMetrics?: unknown) => {
      const data = all.find(item => item.metric_aggregates?.[runRef] || item.metric_artifacts?.[runRef])
      const aggregates = data?.metric_aggregates?.[runRef]
      const artifact = data?.metric_artifacts?.[runRef]
      return <>{taskMetrics !== undefined && <AggregateDetails label="Same-task dispatched calls" value={taskMetrics as Aggregate | undefined} />}<AggregateDetails label="Run worker/fixer usage" value={aggregates?.worker_fixer} /><AggregateDetails label="Run reviewer usage (not task spend)" value={aggregates?.reviewer} /><section><h4>Metric artifact checkpoint</h4><p>Outcome: {artifact?.status ?? 'not recorded'}; path: {artifact?.path ?? 'unavailable'}; SHA: {artifact?.sha ?? 'unavailable'}.</p><p>Separate from the original reviewed code range; this artifact is not independently reviewed application code. Artifact failure does not change execution or review outcome.</p></section></>
    }
    const technical = (children: ReactNode) => <details><summary>Technical references and retained history</summary>{children}</details>
    if (selected.kind === 'edge') {
      const edge = edges.find(item => item.id === selected.id)
      const edgeRun = edge && [...all.flatMap(item => item.tasks), ...all.flatMap(item => item.occurrences), ...all.flatMap(item => item.review_definitions ?? []), ...all.flatMap(item => item.chain ?? [])].find(item => item.ref === edge.source)?.run_ref
      const data = edge?.data as { relation?: string; resolution?: string; qualification?: string; identity?: Record<string, unknown> } | undefined
      const relation = ({ 'declared-prerequisite': 'Declared prerequisite', 'recorded-stop-support': 'Recorded stopping support', chain_trigger: 'Recorded correction trigger', chain_predecessor: 'Recorded correction predecessor', chain_check: 'Recorded correction check', chain_checkpoint: 'Recorded correction checkpoint', 'declared-cross-run-correction': 'Declared cross-run correction' } as Record<string, string>)[data?.relation ?? ''] ?? 'Recorded relation'
      return edge ? <><h3>{relation}</h3><p>{edge.source} → {edge.target}</p><p>{data?.qualification ?? (data?.resolution ? `Qualification: ${data.resolution}.` : 'Qualification not recorded.')}</p>{technical(<><p>Edge ID: {edge.id}</p><p>Relation type: {data?.relation ?? 'unknown'}; resolution: {data?.resolution ?? 'unknown'}.</p><p>Endpoints: {edge.source} → {edge.target}</p><p>Semantic identity: {JSON.stringify(data?.identity ?? {})}</p></>)}{acceptanceDetails(edgeRun ? runFor(edgeRun) : undefined)}</> : null
    }
    const task = all.flatMap(item => item.tasks).find(item => item.ref === selected.id)
    if (task) return <><h3>{taskTitle(task)}</h3><p>Original task label: {task.label}</p><p>Task {task.task_id ?? 'unknown'} · Plan progress: {task.progress?.state ?? 'unknown'}{task.progress?.qualification ? ` — ${task.progress.qualification}` : ''}.</p><p>What happened: {task.summary || 'not recorded'}.</p><p>Current blocker: {task.annotation?.label ?? task.annotation?.code ?? task.reason?.code ?? 'not recorded'}.</p>{acceptanceDetails(runFor(task.run_ref))}{technical(<><p>Task ID: {task.task_id ?? 'unknown'}; plan task {task.ref}; {source(task.run_ref)}.</p><p>Prerequisites: {task.prerequisite_refs.length ? task.prerequisite_refs.join(', ') : 'none'}.</p>{task.reason && <p>Reason: {task.reason.code}; task {task.reason.task_ref ?? 'unknown'}; occurrence {task.reason.occurrence_ref ?? 'unknown'}.</p>}{task.annotation && <p>Annotation: {task.annotation.label ?? task.annotation.code ?? 'recorded'}; occurrence {task.annotation.occurrence_ref ?? 'unknown'}.</p>}</>)}</>
    const definition = all.flatMap(item => item.review_definitions ?? []).find(item => item.ref === selected.id)
    if (definition) return <><h3>{definition.label}</h3><p>Planned review definition — not an agent call.</p>{technical(<p>Definition ID: {definition.ref}; {source(definition.run_ref)}.</p>)}{acceptanceDetails(runFor(definition.run_ref))}</>
    const chain = all.flatMap(item => item.chain ?? []).find(item => item.ref === selected.id)
    if (chain) {
      const chainActivities = all.flatMap(item => item.activities ?? []).filter(activity => activity.run_ref === chain.run_ref && chain.occurrence_refs.includes(activity.occurrence_ref))
      return <><h3>{chain.role === 'fixer' ? 'Fixing agent' : chain.role === 'reviewer' ? `Review ${chain.review_ordinal ?? 'unknown'}` : 'Recorded execution'}</h3><p>Execution outcome: {chain.outcome}.</p><p>What happened: {chain.findings.length ? 'Recorded review findings are available below.' : 'not recorded'}.</p><p>Current blocker: {chain.outcome === 'rejected' ? 'Review rejected the work.' : 'not recorded'}.</p>{chain.findings.length ? <section><h4>Actionable safe findings</h4>{chain.findings.map((finding, index) => <p key={index}>{finding}</p>)}</section> : <p>Actionable safe findings: not recorded.</p>}{technical(<><p>Execution ID: {chain.execution_id}; execution ref {chain.ref}; {source(chain.run_ref)}.</p><p>Explicit trigger: {chain.trigger_ref ?? 'unknown'}; explicit predecessor: {chain.predecessor_ref ?? 'unknown'}.</p><p>Recorded occurrences: {chain.occurrence_refs.length ? chain.occurrence_refs.join(', ') : 'unknown'}.</p><p>Recorded input calls: {chain.input_refs?.length ? chain.input_refs.join(', ') : 'unknown/not recorded'}.</p><p>Range: {chain.review_range.base ?? 'unknown'} → {chain.review_range.head ?? 'unknown'}.</p><p>Commit references: {Object.entries(chain.commit_refs).length ? Object.entries(chain.commit_refs).map(([name, value]) => `${name} ${value}`).join('; ') : 'unknown'}.</p></>)}{chainActivities.length ? <section><h4>Recorded invocation metrics</h4>{chainActivities.map(activity => <MetricDetails key={activity.ref} metrics={activity.metrics as Metrics | undefined} />)}</section> : <MetricDetails metrics={undefined} />}{metricContext(chain.run_ref)}{acceptanceDetails(runFor(chain.run_ref))}</> }
    const activity = all.flatMap(item => item.activities ?? []).find(item => item.ref === selected.id)
    if (activity) {
      const task = activity.task_ref ? all.flatMap(item => item.tasks).find(item => item.ref === activity.task_ref && item.run_ref === activity.run_ref) : undefined
      const title = `${activity.role === 'fixing_worker' ? 'Corrective worker' : activity.role === 'reviewer' ? 'Reviewer' : activity.role === 'worker' ? 'Worker' : 'Recorded activity'}${task ? ` — ${taskTitle(task)}` : ''}${activity.invocation_kind === 'corrective_worker' ? ' (correction)' : ''}`
      const own = all.flatMap(item => item.records).filter(record => activity.record_refs.includes(record.ref) && record.run_ref === activity.run_ref)
      const rendered = graphFor(snapshot, lineage, relations).nodes.find(node => node.id === activity.ref)
      const qualification = rendered?.data.relationQualification
      return <><h3>{title}</h3><p>Execution outcome: {activity.outcome === 'returned' ? 'returned — acceptance not established' : activity.outcome}.</p><p>What happened: {activity.error_category ? `Recorded safe error category: ${activity.error_category}.` : 'not recorded'}.</p><p>Stopping reason: {activity.stopped_by_ref ? `Recorded stopping reference ${activity.stopped_by_ref}.` : 'unknown/not recorded'}.</p>{qualification && <p>Relation qualification: {String(qualification)}</p>}<MetricDetails metrics={activity.metrics as Metrics | undefined} />{metricContext(activity.run_ref, activity.task_metrics)}{technical(<><p>Invocation ID: {activity.invocation_id}; activity {activity.ref}; task {task?.task_id ?? 'unknown'}; {source(activity.run_ref)}.</p><p>Recorded input references: {activity.input_refs.length ? activity.input_refs.join(', ') : 'none'}; qualification {activity.input_qualification}.</p><p>Correction references: {activity.correction_chain.length ? activity.correction_chain.join(', ') : 'none'}; support {activity.support_ref ?? 'unknown'}; stopped by {activity.stopped_by_ref ?? 'unknown'}.</p>{own.map(record => <p key={record.ref}>{recordText(record)}</p>)}</>)}{acceptanceDetails(runFor(activity.run_ref))}<p>Only loaded observations are shown; use history below for retained evidence.</p></>
    }
    const occurrence = all.flatMap(item => item.occurrences).find(item => item.ref === selected.id)
    if (!occurrence) return null
    const own = all.flatMap(item => item.records).filter(item => item.occurrence_ref === occurrence.ref && item.run_ref === occurrence.run_ref)
    const supporting = all.flatMap(item => item.occurrences).filter(item => item.run_ref === occurrence.run_ref && item.role === 'non_model' && (item.support_ref === occurrence.ref || item.parent_ref === occurrence.ref))
    return <><h3>{action(occurrence, all)}</h3><p>Execution outcome: {outcomeText(occurrence, own)}.</p><p>What happened: {own.length ? 'Recorded lifecycle evidence is available in technical references.' : 'not recorded'}.</p><p>Current blocker: {occurrence.stopping ? 'Recorded workflow stopping step.' : 'not recorded'}.</p>{occurrence.execution_summary?.qualification && <p>Recorded execution qualification: {occurrence.execution_summary.qualification}.</p>}{technical(<><p>Occurrence ID: {occurrence.occurrence_id ?? 'unknown'}; execution {occurrence.ref}{occurrence.task_ref ? `; task ${occurrence.task_ref}` : ''}; {source(occurrence.run_ref)}.</p>{own.map(item => <p key={item.ref}>{recordText(item)}</p>)}{supporting.map(item => <section key={item.ref}><h4>{action(item, all)}: {outcomeText(item, all.flatMap(value => value.records))}</h4><p>{item.ref}; {item.stopping ? 'workflow stopping step' : 'supporting observation'}</p>{all.flatMap(value => value.records).filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref).map(record => <p key={record.ref}>{recordText(record)}</p>)}</section>)}</>)}{acceptanceDetails(runFor(occurrence.run_ref))}<p>Only loaded observations are shown; use history below for retained evidence.</p></>
  }, [edges, lineage, selected, snapshot])
  // ReactFlow retains measured dimensions/handles by node identity. Recreating nodes
  // on viewport moves hides calls and removes connectors until ResizeObserver reruns.
  const renderedNodes = useMemo(() => nodes.map(node => node.id.startsWith('group:') ? node : ({ ...node, selected: selected?.kind === 'node' && selected.id === node.id, data: { ...node.data, label: <>
    <strong>{String(node.data.label)}</strong>
    <small>{String(node.data.status)}</small>
    </> } })), [nodes, selected])
  const allOccurrences = snapshot ? [snapshot, ...lineage].flatMap(item => item.occurrences) : []; const failures = allOccurrences.filter(item => item.outcome === 'failed').length; const incomplete = allOccurrences.filter(item => item.completeness === 'incomplete').length; const allTasks = [snapshot, ...lineage].flatMap(value => value?.tasks ?? []); const waiting = allTasks.filter(task => task.annotation?.code === 'waiting_for_input').length + allOccurrences.filter(item => !allTasks.some(task => task.ref === item.task_ref) && status(item, [snapshot, ...lineage].flatMap(value => value?.records ?? [])) === 'waiting').length
  const selectedRunInfo = runs.find(run => run.ref === selectedRun); const acceptance = selectedRunInfo?.review_acceptance; const acceptanceText = acceptance?.state === 'accepted_full_range' ? `Full-range acceptance: ${acceptance.base} → ${acceptance.head}` : acceptance?.state === 'correction_only' ? 'Correction-only review; current head is not accepted.' : 'Current lineage acceptance is unknown.'
  const freshness = snapshot?.observation; const freshnessText = freshness ? `Read ${freshness.read_state}; last successful read ${freshness.last_success_at ?? 'unknown'}; last recorded activity ${freshness.last_recorded_at ?? 'unknown'}${freshness.warnings.length ? `; warning: ${freshness.warnings.join(', ')}` : ''}.` : 'Read state unknown.'
  const runnerText = selectedRunInfo?.runner_state ? `Recorded runner ${selectedRunInfo.runner_state.state}${selectedRunInfo.runner_state.reason ? ` (${selectedRunInfo.runner_state.reason})` : ''}; process presence does not prove progress.` : 'Recorded runner unknown.'
  return <main>
    <aside aria-label="Recorded runs">
    <h1>Workflow monitor</h1>
    <p className="status" role="status">{message}</p>
    <h2>Runs</h2>
    <label className="run-filter">Filter run ID <input value={filter} onChange={event => setFilter(event.target.value)} placeholder="Filter run ID" /></label>
    <div className="run-list">{runs.filter(run => run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())).map(run => <button key={run.ref} className={run.ref === selectedRun ? 'selected' : ''} onClick={() => { if (run.ref === selectedRun) return; window.history.pushState(null, '', routeFor(run.display_id)); applyLocation(runsRef.current) }}>{run.label} · {run.display_id} · {run.completeness}</button>)}</div>
    {filter && !runs.some(run => run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())) && <p>No run IDs match this filter.</p>}
    {filter && selectedRun && !runs.some(run => run.ref === selectedRun && run.display_id.toLocaleLowerCase().includes(filter.toLocaleLowerCase())) && <p>The selected run is outside this filter.</p>}
    </aside>
    <section className="viewer">
    <header>
    <h2>Selected run graph</h2>
    <p aria-label="Selected run">Selected run: {selectedRunInfo?.display_id ?? 'unknown'} · ID: {selectedRun ?? 'unknown'}</p>
    <p>Pan and zoom the graph. Select a node or edge for its brief details.</p>
    </header>
    <div className="legend" aria-label="Status legend">
    <span className="success">Green: execution returned</span>
    <span className="failed">Red: execution failure / stopping step</span>
    <span className="waiting">Amber: waiting (not dependency-blocked)</span>
    <span className="neutral">Recorded running / incomplete / unknown</span>
    <span className="plan">Plan progress (not execution outcome or acceptance)</span>
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
    <p>{relations.length ? `Declared followups: ${relations.map(item => `${item.resolution}: ${item.source_run_ref} → ${item.run_ref}`).join('; ')}` : 'No declared followups.'}</p>
    <p>{snapshot ? `Inventory: ${snapshot.inventory.total_count ?? snapshot.inventory.observation_count} total, ${snapshot.inventory.loaded_count ?? snapshot.records.length} loaded, ${snapshot.inventory.hidden_count} hidden, ${snapshot.inventory.unsupported_count ?? 0} unsupported.` : 'Inventory unavailable.'}</p>{snapshot && <p>Inventory: {snapshot.inventory.observation_count} records, {snapshot.inventory.occurrence_count} occurrences, {snapshot.inventory.phase_count} phases; {snapshot.inventory.hidden_count} hidden.</p>}<p aria-label="Collapsed history badges">{failures} failed; {waiting} waiting; {incomplete} incomplete.</p>{snapshot && <details>
    <summary>Loaded history and technical references</summary>{[snapshot, ...lineage].map(item => <section key={item.snapshot_ref ?? item.runs[0]?.ref}>
    <h3>Source {item.records[0]?.run_ref ?? 'selected snapshot'}</h3>{item.phases.map(phase => <p key={phase.ref}>{phase.label}; definition {phase.ref}</p>)}{item.tasks.map(task => <p key={task.ref}>{task.label}: {task.summary}; plan progress {task.progress?.state ?? 'unavailable'}; {task.ref}</p>)}{item.occurrences.map(occurrence => <p key={occurrence.ref}>{action(occurrence, [item])}; {outcomeText(occurrence, item.records)}; {occurrence.ref}</p>)}{item.records.map(record => <p key={record.ref}>{recordText(record)}; source {record.run_ref}</p>)}{item.unknown_records?.map(record => <p key={record.ref}>unsupported {record.code}; {record.ref}; source {record.run_ref}; sequence {record.source_seq ?? 'unknown'}</p>)}</section>)}</details>}{lineage.filter(item => item.next_cursor).map(item => <button key={item.snapshot_ref} onClick={() => void loadLinkedMore(item)}>Load correction history {item.occurrences[0]?.run_ref}</button>)}{snapshot?.next_cursor && <button onClick={() => void loadMore()}>Load more history</button>}</section>
    </section>
    </main>
}
createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
