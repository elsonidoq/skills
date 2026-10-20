import { StrictMode, useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import ELK from 'elkjs/lib/elk.bundled.js'
import { Background, Controls, ReactFlow, type Edge, type Node, type Viewport } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './style.css'

type Run = { ref: string; label: string; started_at: number | null; completeness: string }
type Observation = { ref: string; run_ref: string; occurrence_ref: string; kind: string; source_seq: number; recorded_at: number | null; exit_code: number | null; finding_count: number | null; review_base: string | null; review_head: string | null }
type Occurrence = { ref: string; run_ref: string; phase_ref: string; task_ref: string | null; role: string; outcome: string | null; completeness: string; record_refs: string[] }
type GraphEdge = { ref: string; run_ref: string; type: string; from_ref: string; to_ref: string; resolution: string }
type Snapshot = { runs: Run[]; phases: Array<{ ref: string; run_ref: string; label: string }>; tasks: Array<{ ref: string; run_ref: string; label: string; summary: string }>; occurrences: Occurrence[]; records: Observation[]; edges: GraphEdge[]; inventory: { phase_count: number; occurrence_count: number; observation_count: number; hidden_count: number } }

type Graph = { nodes: Node[]; edges: Edge[]; topology: string }

const headers = { 'X-Workflow-Monitor': '1' }
const elk = new ELK()
const edgeLabels: Record<string, string> = { possible_flow: 'Possible flow', task_prerequisite: 'Task prerequisite', recorded_next: 'Recorded sequence', phase_occurrence: 'Phase occurrence', execution_milestone: 'Execution milestone', reviewed_range: 'Reviewed range', declared_correction: 'Declared correction' }

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path, { headers })
  if (!response.ok) throw new Error('The monitor snapshot is unavailable.')
  return response.json() as Promise<T>
}

function graphFor(snapshot: Snapshot, selectedRun: string): Graph {
  const records = snapshot.records.filter(record => record.run_ref === selectedRun)
  const occurrences = snapshot.occurrences.filter(item => item.run_ref === selectedRun)
  const anchors = [...snapshot.phases.filter(item => item.run_ref === selectedRun), ...snapshot.tasks.filter(item => item.run_ref === selectedRun)]
  const nodes: Node[] = [
    ...anchors.map(item => ({ id: item.ref, position: { x: 0, y: 0 }, data: { label: item.label }, className: 'anchor-node' })),
    ...occurrences.map(item => ({ id: item.ref, position: { x: 0, y: 0 }, data: { label: `${item.role}: ${item.outcome ?? 'recorded'}` }, className: `occurrence-node ${item.outcome === 'failed' ? 'failed' : ''}` })),
    ...records.map(item => ({ id: item.ref, position: { x: 0, y: 0 }, data: { label: `${item.kind} #${item.source_seq}` }, className: item.kind === 'failed' ? 'failed' : 'record-node' }))
  ]
  const ids = new Set(nodes.map(node => node.id))
  const edges = snapshot.edges.filter(item => item.run_ref === selectedRun && ids.has(item.from_ref) && ids.has(item.to_ref)).map(item => ({ id: item.ref, source: item.from_ref, target: item.to_ref, label: edgeLabels[item.type] ?? item.type, type: 'smoothstep', animated: item.type === 'recorded_next' }))
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.id, edge.source, edge.target]).sort() }) }
}

function App() {
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedRun, setSelectedRun] = useState<string | null>(null)
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selected, setSelected] = useState<{ kind: 'node' | 'edge'; id: string } | null>(null)
  const [viewport, setViewport] = useState<Viewport>({ x: 0, y: 0, zoom: 1 })
  const [message, setMessage] = useState('Loading monitor…')
  const fetchGeneration = useRef(0)
  const layoutGeneration = useRef(0)
  const topology = useRef<string | null>(null)
  const positions = useRef<Record<string, { x: number; y: number }>>({})

  useEffect(() => {
    let active = true
    const loadRuns = async () => {
      try {
        const data = await getJson<{ runs: Run[] }>('/api/monitor/v1/runs')
        if (!active) return
        setRuns(data.runs)
        setSelectedRun(current => current && data.runs.some(run => run.ref === current) ? current : (data.runs[0]?.ref ?? null))
      } catch (error) { if (active) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') }
    }
    void loadRuns()
    const timer = window.setInterval(() => void loadRuns(), 2000)
    return () => { active = false; window.clearInterval(timer) }
  }, [])

  useEffect(() => {
    if (!selectedRun) return
    const generation = ++fetchGeneration.current
    let active = true
    const loadSnapshot = async () => {
      try {
        const data = await getJson<Snapshot>(`/api/monitor/v1/runs/${encodeURIComponent(selectedRun)}/snapshot`)
        if (active && generation === fetchGeneration.current) { setSnapshot(data); setMessage('Updated from the recorded snapshot.') }
      } catch (error) { if (active && generation === fetchGeneration.current) setMessage(error instanceof Error ? error.message : 'The monitor snapshot is unavailable.') }
    }
    void loadSnapshot()
    const timer = window.setInterval(() => void loadSnapshot(), 2000)
    return () => { active = false; window.clearInterval(timer); ++fetchGeneration.current }
  }, [selectedRun])

  useEffect(() => {
    if (!snapshot || !selectedRun) return
    const graph = graphFor(snapshot, selectedRun)
    const known = new Set([...graph.nodes.map(node => node.id), ...graph.edges.map(edge => edge.id)])
    setSelected(current => current && known.has(current.id) ? current : null)
    setEdges(graph.edges)
    if (topology.current === graph.topology) {
      setNodes(graph.nodes.map(node => ({ ...node, position: positions.current[node.id] ?? node.position })))
      return
    }
    topology.current = graph.topology
    const generation = ++layoutGeneration.current
    let active = true
    void elk.layout({ id: 'monitor', layoutOptions: { 'elk.algorithm': 'layered', 'elk.direction': 'RIGHT', 'elk.spacing.nodeNode': '40', 'elk.layered.spacing.nodeNodeBetweenLayers': '100' }, children: graph.nodes.map(node => ({ id: node.id, width: 180, height: 54 })), edges: graph.edges.map(edge => ({ id: edge.id, sources: [edge.source], targets: [edge.target] })) }).then(layout => {
      if (!active || generation !== layoutGeneration.current) return
      const laidOut = graph.nodes.map(node => {
        const result = layout.children?.find(child => child.id === node.id)
        const position = { x: result?.x ?? 0, y: result?.y ?? 0 }
        positions.current[node.id] = position
        return { ...node, position }
      })
      setNodes(laidOut)
    })
    return () => { active = false }
  }, [selectedRun, snapshot])

  const details = useMemo(() => {
    if (!snapshot || !selectedRun || !selected) return null
    if (selected.kind === 'node') {
      const occurrence = snapshot.occurrences.find(item => item.run_ref === selectedRun && item.ref === selected.id)
      const record = snapshot.records.find(item => item.run_ref === selectedRun && item.ref === selected.id)
      return occurrence ? `${occurrence.role}; ${occurrence.outcome ?? occurrence.completeness}` : record ? `${record.kind}; sequence ${record.source_seq}${record.exit_code !== null ? `; exit ${record.exit_code}` : ''}` : null
    }
    const edge = snapshot.edges.find(item => item.run_ref === selectedRun && item.ref === selected.id)
    return edge ? `${edgeLabels[edge.type] ?? edge.type}; ${edge.resolution}` : null
  }, [selected, selectedRun, snapshot])

  return <main>
    <aside aria-label="Recorded runs"><h1>Workflow monitor</h1><p className="status" role="status">{message}</p><h2>Runs</h2><div className="run-list">{runs.map(run => <button key={run.ref} className={run.ref === selectedRun ? 'selected' : ''} onClick={() => { ++fetchGeneration.current; ++layoutGeneration.current; topology.current = null; setSnapshot(null); setSelectedRun(run.ref); setSelected(null) }}>{run.label} · {run.completeness}</button>)}</div></aside>
    <section className="viewer"><header><h2>Selected run graph</h2><p>Pan and zoom the graph. Select a node or edge for its brief details.</p></header><div className="legend" aria-label="Edge legend">{Object.entries(edgeLabels).map(([type, label]) => <span key={type}>{label}</span>)}</div><div className="graph" aria-label="Workflow graph"><ReactFlow nodes={nodes} edges={edges} viewport={viewport} onMoveEnd={(_, next) => setViewport(next)} onNodeClick={(_, node) => setSelected({ kind: 'node', id: node.id })} onEdgeClick={(_, edge) => setSelected({ kind: 'edge', id: edge.id })}><Background /><Controls /></ReactFlow></div><section className="details" aria-live="polite"><h2>Details</h2><p>{details ?? 'Select a graph node or edge.'}</p><p>{snapshot ? `Inventory: ${snapshot.inventory.observation_count} records, ${snapshot.inventory.occurrence_count} occurrences, ${snapshot.inventory.phase_count} phases; ${snapshot.inventory.hidden_count} hidden.` : 'Inventory unavailable.'}</p></section></section>
  </main>
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
