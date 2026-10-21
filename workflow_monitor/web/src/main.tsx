import { StrictMode, useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import ELK from 'elkjs/lib/elk.bundled.js'
import { Background, Controls, ReactFlow, type Edge, type Node, type Viewport, type ReactFlowInstance } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './style.css'
import { graphFor, action, status, outcomeText, recordText, type Observation, type Occurrence, type Followup, type PlannedTask, type ReviewDefinition } from './graph'

type Acceptance = { state: string; base: string | null; head: string | null }
type AcceptanceItem = { occurrence_ref: string; state: string; ordinal?: number | null; exit_code?: number | null; baseline?: string | null; head?: string | null; no_change?: boolean | null; approved?: boolean | null; finding_count?: number | null; base?: string | null }
type AcceptanceSummary = { checks: AcceptanceItem[]; checkpoints: AcceptanceItem[]; reviews: AcceptanceItem[]; full_range: Acceptance }
type RunnerState = { state: 'live' | 'stopped' | 'unknown'; reason: string | null }
type Run = { ref: string; display_id: string; label: string; started_at: number | null; completeness: string; plan_availability?: string; runner_state?: RunnerState; review_acceptance?: Acceptance; acceptance_summary?: AcceptanceSummary }
type Unknown = { ref: string; run_ref: string; source_seq: number | null; code: string }
type GraphEdge = { ref: string; run_ref: string; type: string; from_ref: string; to_ref: string; resolution: string }
type Inventory = { phase_count: number; occurrence_count: number; observation_count: number; total_count: number; loaded_count: number; hidden_count: number; unsupported_count: number }
type Freshness = { read_at: number; last_success_at: number | null; last_recorded_at: number | null; read_state: 'current' | 'unavailable'; warnings: string[] }
type Snapshot = { runs: Run[]; phases: Array<{ ref: string; run_ref: string; label: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; unknown_records: Unknown[]; edges: GraphEdge[]; inventory: Inventory; snapshot_ref: string; next_cursor: string | null; observation?: Freshness }
const POLL_INTERVAL_MS = 60_000
const headers = { 'X-Workflow-Monitor': '1' }
const elk = new ELK()
async function getJson<T>(path: string): Promise<T> { const response = await fetch(path, { headers }); if (!response.ok) throw new Error(response.status === 409 ? 'The snapshot changed; refreshing history.' : 'The monitor snapshot is unavailable.'); return response.json() as Promise<T> }
function source(runRef: string) { return `source ${runRef}` }
function mergePage(current: Snapshot | null, page: Snapshot): Snapshot {
  if (!current || current.snapshot_ref !== page.snapshot_ref) return page
  const records = [...current.records, ...page.records.filter(item => !current.records.some(old => old.ref === item.ref))]
  const oldUnknown = current.unknown_records ?? []; const pageUnknown = page.unknown_records ?? []
  const unknown_records = [...oldUnknown, ...pageUnknown.filter(item => !oldUnknown.some(old => old.ref === item.ref))]
  return { ...page, next_cursor: current.next_cursor, records, unknown_records, inventory: { ...page.inventory, loaded_count: records.length + unknown_records.length, hidden_count: Math.max(0, page.inventory.total_count - records.length - unknown_records.length) } }
}
function App() {
  const [runs, setRuns] = useState<Run[]>([]); const [selectedRun, setSelectedRun] = useState<string | null>(null); const [snapshot, setSnapshot] = useState<Snapshot | null>(null); const [lineage, setLineage] = useState<Snapshot[]>([]); const [relations, setRelations] = useState<Followup[]>([]); const [nodes, setNodes] = useState<Node[]>([]); const [edges, setEdges] = useState<Edge[]>([]); const [selected, setSelected] = useState<{ kind: 'node' | 'edge'; id: string } | null>(null); const [viewport, setViewport] = useState<Viewport>({ x: 0, y: 0, zoom: 1 }); const [message, setMessage] = useState('Loading monitor…')
  const flow = useRef<ReactFlowInstance | null>(null); const fitPending = useRef(false);
  const fetchGeneration = useRef(0); const layoutGeneration = useRef(0); const topology = useRef<string | null>(null); const positions = useRef<Record<string, { x: number; y: number }>>({})
  useEffect(() => { let active = true; const loadRuns = async () => { try { const data = await getJson<{ runs: Run[] }>('/api/monitor/v1/runs'); if (!active) return; setRuns(data.runs); setSelectedRun(current => current && data.runs.some(run => run.ref === current) ? current : (data.runs[0]?.ref ?? null)) } catch (error) { if (active) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') } }; void loadRuns(); const timer = window.setInterval(() => void loadRuns(), POLL_INTERVAL_MS); return () => { active = false; window.clearInterval(timer) } }, [])
  useEffect(() => { if (!selectedRun) return; const generation = ++fetchGeneration.current; let active = true; const loadSnapshot = async () => { try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/snapshot`); let followups: Followup[] = []; try { let cursor: string | null = null; do { const result: { followups: Followup[]; next_cursor?: string | null } = await getJson(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/followups?snapshot=${encodeURIComponent(page.snapshot_ref)}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ''}`); followups.push(...result.followups); cursor = result.next_cursor ?? null } while (cursor) } catch { /* A snapshot remains usable when a prior closed fixture has no followup route. */ } const linkedRefs = [...new Set(followups.flatMap(item => [item.run_ref, item.source_run_ref]).filter(ref => ref !== selectedRun))]; const linked = (await Promise.all(linkedRefs.map(async ref => { try { return await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(ref)}/snapshot`) } catch { return null } }))).filter((item): item is Snapshot => item !== null); if (active && generation === fetchGeneration.current) { setSnapshot(current => mergePage(current, page)); setRelations(followups); setLineage(current => linked.map(item => mergePage(current.find(old => old.snapshot_ref === item.snapshot_ref) ?? null, item))); setMessage('Updated from the recorded snapshot.') } } catch (error) { if (active && generation === fetchGeneration.current) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') } }; void loadSnapshot(); const timer = window.setInterval(() => void loadSnapshot(), POLL_INTERVAL_MS); return () => { active = false; window.clearInterval(timer); ++fetchGeneration.current } }, [selectedRun])
  const loadMore = async () => { if (!snapshot || !selectedRun || !snapshot.next_cursor) return; const generation = fetchGeneration.current; try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/history?snapshot=${encodeURIComponent(snapshot.snapshot_ref)}&cursor=${encodeURIComponent(snapshot.next_cursor)}`); if (generation === fetchGeneration.current) setSnapshot(current => ({ ...mergePage(current, page), next_cursor: page.next_cursor })) } catch (error) { if (generation !== fetchGeneration.current) return; setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.'); try { const fresh = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/snapshot`); if (generation === fetchGeneration.current) setSnapshot(fresh) } catch { /* Keep the last safe view on read failure. */ } } }
  const loadLinkedMore = async (linked: Snapshot) => {
    const ref = linked.occurrences[0]?.run_ref ?? linked.records[0]?.run_ref ?? linked.unknown_records[0]?.run_ref
    if (!ref || !linked.next_cursor) return
    const generation = fetchGeneration.current
    try { const page = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(ref)}/history?snapshot=${encodeURIComponent(linked.snapshot_ref)}&cursor=${encodeURIComponent(linked.next_cursor)}`); if (generation === fetchGeneration.current) setLineage(current => current.map(item => item.snapshot_ref === linked.snapshot_ref ? { ...mergePage(item, page), next_cursor: page.next_cursor } : item)) } catch (error) { if (generation === fetchGeneration.current) setMessage(error instanceof Error ? error.message : 'History unavailable.') }
  }
  useEffect(() => { if (!snapshot || !selectedRun) return; const graph = graphFor(snapshot, lineage, relations); const known = new Set([...graph.nodes.map(node => node.id), ...graph.edges.map(edge => edge.id)]); setSelected(current => current && known.has(current.id) ? current : null); setEdges(graph.edges); if (topology.current === graph.topology) { setNodes(graph.nodes.map(node => ({ ...node, position: positions.current[node.id] ?? node.position }))); return } fitPending.current = true; const generation = ++layoutGeneration.current; let active = true; void elk.layout({ id: 'monitor', layoutOptions: { 'elk.algorithm': 'layered', 'elk.direction': 'RIGHT', 'elk.spacing.nodeNode': '25', 'elk.layered.spacing.nodeNodeBetweenLayers': '60' }, children: graph.nodes.map(node => ({ id: node.id, width: 180, height: 70 })), edges: graph.edges.map(edge => ({ id: edge.id, sources: [edge.source], targets: [edge.target] })) }).then(layout => { if (!active || generation !== layoutGeneration.current) return; topology.current = graph.topology; setNodes(graph.nodes.map(node => { const result = layout.children?.find(child => child.id === node.id); const position = { x: result?.x ?? 0, y: result?.y ?? 0 }; positions.current[node.id] = position; return { ...node, position } })) }); return () => { active = false } }, [selectedRun, snapshot, lineage, relations])
  useEffect(() => { if (nodes.length && fitPending.current && flow.current) { fitPending.current = false; void flow.current.fitView({ padding: .15, maxZoom: 1, minZoom: .25 }) } }, [nodes])
  const details = useMemo(() => {
    if (!snapshot || !selected) return null
    const all = [snapshot, ...lineage]
    const runFor = (ref: string) => all.flatMap(item => item.runs).find(run => run.ref === ref)
    const acceptanceDetails = (run: Run | undefined) => {
      const summary = run?.acceptance_summary
      if (!summary) return <p>Full retained acceptance summary unavailable.</p>
      const full = summary.full_range
      return <section><h4>Acceptance (full retained summary)</h4><p>Full-range qualification: {full?.state ?? 'unknown'}{full?.base && full?.head ? `; ${full.base} → ${full.head}` : ''}</p>{summary.checks.map(item => <p key={`check-${item.occurrence_ref}`}>Check {item.occurrence_ref}: {item.state}; ordinal {item.ordinal ?? 'unknown'}; exit {item.exit_code ?? 'unknown'}</p>)}{summary.checkpoints.map(item => <p key={`checkpoint-${item.occurrence_ref}`}>Checkpoint {item.occurrence_ref}: {item.state}; {item.baseline ?? 'unknown'} → {item.head ?? 'unknown'}; no change {String(item.no_change ?? 'unknown')}</p>)}{summary.reviews.map(item => <p key={`review-${item.occurrence_ref}`}>Review {item.occurrence_ref}: {item.state}; approved {String(item.approved ?? 'unknown')}; findings {item.finding_count ?? 'unknown'}; range {item.base ?? 'unknown'} → {item.head ?? 'unknown'}</p>)}</section>
    }
    if (selected.kind === 'edge') { const edge = edges.find(item => item.id === selected.id); const edgeRun = edge && [...all.flatMap(item => item.tasks), ...all.flatMap(item => item.occurrences), ...all.flatMap(item => item.review_definitions ?? [])].find(item => item.ref === edge.source)?.run_ref; return edge ? <><h3>{String(edge.label)}</h3><p>Recorded relation: {edge.source} → {edge.target}; {String(edge.label) === 'Recorded sequence' ? 'recorded order, not proof of causality.' : 'declared or recorded as labelled.'}</p><p>Edge {edge.id}</p>{acceptanceDetails(edgeRun ? runFor(edgeRun) : undefined)}</> : null }
    const task = all.flatMap(item => item.tasks).find(item => item.ref === selected.id)
    if (task) return <><h3>{task.label}</h3><p>Task ID: {task.task_id ?? 'unknown'}</p><p>Plan task {task.ref}; {source(task.run_ref)}</p><p>Progress: {task.progress?.state ?? 'unavailable'}{task.progress?.qualification ? ` — ${task.progress.qualification}` : ''}.</p><p>Prerequisites: {task.prerequisite_refs.length ? task.prerequisite_refs.join(', ') : 'none'}.</p>{task.reason && <p>Reason: {task.reason.code}{task.reason.task_ref ? `; task ${task.reason.task_ref}` : ''}{task.reason.occurrence_ref ? `; occurrence ${task.reason.occurrence_ref}` : ''}.</p>}{task.annotation && <p>Annotation: {task.annotation.label ?? task.annotation.code ?? 'recorded'}{task.annotation.occurrence_ref ? `; occurrence ${task.annotation.occurrence_ref}` : ''}.</p>}<p>{task.summary}</p>{acceptanceDetails(runFor(task.run_ref))}</>
    const definition = all.flatMap(item => item.review_definitions ?? []).find(item => item.ref === selected.id)
    if (definition) return <><h3>{definition.label}</h3><p>Plan definition {definition.ref}; {source(definition.run_ref)}. This is not an agent call.</p>{acceptanceDetails(runFor(definition.run_ref))}</>
    const occurrence = all.flatMap(item => item.occurrences).find(item => item.ref === selected.id)
    if (!occurrence) return null
    const own = all.flatMap(item => item.records).filter(item => item.occurrence_ref === occurrence.ref && item.run_ref === occurrence.run_ref)
    const supporting = all.flatMap(item => item.occurrences).filter(item => item.run_ref === occurrence.run_ref && item.role === 'non_model' && (item.support_ref === occurrence.ref || item.parent_ref === occurrence.ref))
    return <><h3>{action(occurrence, all)}</h3><p>{occurrence.role}; {outcomeText(occurrence, own)}; {source(occurrence.run_ref)}</p><p>Occurrence ID: {occurrence.occurrence_id ?? 'unknown'}</p><p>Execution {occurrence.ref}{occurrence.task_ref ? `; task ${occurrence.task_ref}` : ''}</p>{own.map(item => <p key={item.ref}>{recordText(item)}</p>)}{supporting.map(item => <section key={item.ref}><h4>{action(item, all)}: {outcomeText(item, all.flatMap(value => value.records))}</h4><p>{item.ref}; {item.stopping ? 'workflow stopping step' : 'supporting observation'}</p>{all.flatMap(value => value.records).filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref).map(record => <p key={record.ref}>{recordText(record)}</p>)}</section>)}{acceptanceDetails(runFor(occurrence.run_ref))}<p>Only loaded observations are shown; use history below for retained evidence.</p></>
  }, [edges, lineage, selected, snapshot])
  const allOccurrences = snapshot ? [snapshot, ...lineage].flatMap(item => item.occurrences) : []; const failures = allOccurrences.filter(item => item.outcome === 'failed').length; const incomplete = allOccurrences.filter(item => item.completeness === 'incomplete').length; const waiting = allOccurrences.filter(item => status(item, [snapshot, ...lineage].flatMap(value => value?.records ?? [])) === 'waiting').length
  const selectedRunInfo = runs.find(run => run.ref === selectedRun); const acceptance = selectedRunInfo?.review_acceptance; const acceptanceText = acceptance?.state === 'accepted_full_range' ? `Full-range acceptance: ${acceptance.base} → ${acceptance.head}` : acceptance?.state === 'correction_only' ? 'Correction-only review; current head is not accepted.' : 'Current lineage acceptance is unknown.'
  const freshness = snapshot?.observation; const freshnessText = freshness ? `Read ${freshness.read_state}; last successful read ${freshness.last_success_at ?? 'unknown'}; last recorded activity ${freshness.last_recorded_at ?? 'unknown'}${freshness.warnings.length ? `; warning: ${freshness.warnings.join(', ')}` : ''}.` : 'Read state unknown.'
  const runnerText = selectedRunInfo?.runner_state ? `Recorded runner ${selectedRunInfo.runner_state.state}${selectedRunInfo.runner_state.reason ? ` (${selectedRunInfo.runner_state.reason})` : ''}; process presence does not prove progress.` : 'Recorded runner unknown.'
  return <main>
    <aside aria-label="Recorded runs">
    <h1>Workflow monitor</h1>
    <p className="status" role="status">{message}</p>
    <h2>Runs</h2>
    <div className="run-list">{runs.map(run => <button key={run.ref} className={run.ref === selectedRun ? 'selected' : ''} onClick={() => { if (run.ref === selectedRun) return; setNodes([]); setEdges([]); ++fetchGeneration.current; ++layoutGeneration.current; topology.current = null; setSnapshot(null); setLineage([]); setRelations([]); setSelectedRun(run.ref); setSelected(null) }}>{run.label} · {run.display_id} · {run.completeness}</button>)}</div>
    </aside>
    <section className="viewer">
    <header>
    <h2>Selected run graph</h2>
    <p aria-label="Selected run">Selected run: {selectedRunInfo?.display_id ?? 'unknown'}</p>
    <p>Pan and zoom the graph. Select a node or edge for its brief details.</p>
    </header>
    <div className="legend" aria-label="Status legend">
    <span className="success">Green: execution returned</span>
    <span className="failed">Red: execution failure / stopping step</span>
    <span className="waiting">Amber: waiting (not dependency-blocked)</span>
    <span className="neutral">Recorded running / incomplete / unknown</span>
    <span className="plan">Plan progress (not execution outcome or acceptance)</span>
    <span className="acceptance">Acceptance is in Details; skipped/cancelled unsupported</span>
    <span>Declared prerequisite · Recorded attachment · Recorded sequence · Declared correction</span>
    {snapshot && selectedRunInfo?.plan_availability !== 'complete' && <span className="unavailable">Complete graph unavailable</span>}
    </div>
    <div className="execution-view">
    <div className="graph" aria-label="Workflow graph">
    <ReactFlow<Node, Edge> nodes={nodes.map(node => ({ ...node, selected: selected?.kind === 'node' && selected.id === node.id, data: { ...node.data, label: <>
    <strong>{String(node.data.label)}</strong>
    <small>{String(node.data.status)}</small>
    </> } }))} edges={edges.map(edge => ({ ...edge, selected: selected?.kind === 'edge' && selected.id === edge.id }))} onInit={instance => { flow.current = instance }} minZoom={.15} viewport={viewport} onMoveEnd={(_, next) => setViewport(next)} onNodeClick={(_, node) => setSelected({ kind: 'node', id: node.id })} onEdgeClick={(_, edge) => setSelected({ kind: 'edge', id: edge.id })}>
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
