import type { Edge, Node } from '@xyflow/react'
export type Observation = { ref: string; run_ref: string; occurrence_ref: string; kind: string; source_seq: number; recorded_at: number | null; ordinal?: number | null; exit_code: number | null; finding_count: number | null; approved?: boolean | null; no_change?: boolean | null; baseline?: string | null; head?: string | null; review_base: string | null; review_head: string | null }
export type Occurrence = { ref: string; run_ref: string; phase_ref: string; task_ref: string | null; role: string; outcome: string | null; completeness: string; record_refs: string[]; phase?: string; first_seq?: number; last_seq?: number; parent_ref?: string | null; support_ref?: string | null; stopping?: boolean }
export type GraphSnapshot = { tasks: Array<{ ref: string; run_ref: string; label: string; summary: string }>; occurrences: Occurrence[]; records: Observation[] }
export type Followup = { run_ref: string; source_run_ref: string; review_occurrence_ref: string; resolution: string }
export function action(item: Occurrence, snapshots: GraphSnapshot[]) {
  const verb = item.role === 'worker' ? 'Implement' : item.role === 'fixing_worker' ? 'Fix' : item.role === 'reviewer' ? 'Review' : ({ check: 'Check', checkpoint: 'Checkpoint', prepare: 'Prepare', gate: 'Gate', terminal: 'Stop' }[item.phase ?? ''] ?? 'Stop')
  const task = snapshots.flatMap(snapshot => snapshot.tasks).find(task => task.ref === item.task_ref && task.run_ref === item.run_ref)
  return `${verb}${task ? ` ${task.label.length > 24 ? task.label.slice(0, 23) + '…' : task.label}` : ''}`
}
export function status(item: Occurrence, records: Observation[]) {
  const own = records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref)
  if (item.outcome === 'failed' || own.some(record => record.kind === 'failed' || record.kind === 'delivery_failed')) return 'failed'
  if (item.outcome === 'passed') return 'success'
  if (own.some(record => record.kind === 'question_requested') && !own.some(record => record.kind === 'answer_sent' || record.kind === 'answer_returned')) return 'waiting'
  return 'neutral'
}
export function outcomeText(item: Occurrence, records: Observation[]) {
  if (item.outcome) return item.outcome
  const own = records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref)
  if (own.some(record => record.kind === 'returned')) return 'returned — acceptance not established'
  return item.completeness === 'incomplete' ? 'incomplete — outcome unknown' : 'recorded — outcome unknown'
}
export function graphFor(root: GraphSnapshot, lineage: GraphSnapshot[], relations: Followup[]) {
  const snapshots = [root, ...lineage], occurrences = snapshots.flatMap(item => item.occurrences), records = snapshots.flatMap(item => item.records)
  const visible = occurrences.filter(item => ['worker', 'fixing_worker', 'reviewer'].includes(item.role) || item.stopping)
  const nodes: Node[] = visible.map(item => {
    const ownStatus = status(item, records)
    const pendingQuestion = occurrences.some(child => child.run_ref === item.run_ref && child.parent_ref === item.ref && status(child, records) === 'waiting')
    const color = item.stopping ? 'failed' : ownStatus === 'neutral' && pendingQuestion ? 'waiting' : ownStatus
    return { id: item.ref, position: { x: 0, y: 0 }, data: { label: action(item, snapshots), status: color === 'waiting' ? 'waiting — recorded question' : outcomeText(item, records) }, className: `execution-node ${color}` }
  })
  const edges: Edge[] = []
  const seq = (item: Occurrence) => item.first_seq ?? Math.min(...records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref).map(record => record.source_seq))
  for (const run of new Set(visible.map(item => item.run_ref))) {
    const agents = visible.filter(item => item.run_ref === run && item.role !== 'non_model').sort((a, b) => seq(a) - seq(b))
    for (let index = 1; index < agents.length; index++) edges.push({ id: `sequence_${agents[index - 1].ref}_${agents[index].ref}`, source: agents[index - 1].ref, target: agents[index].ref, label: 'Recorded sequence', type: 'smoothstep' })
    for (const stop of visible.filter(item => item.run_ref === run && item.stopping)) {
      const parent = agents.find(item => item.ref === stop.support_ref)
      if (parent) edges.push({ id: `stop_${stop.ref}`, source: parent.ref, target: stop.ref, label: 'Stopping step', type: 'smoothstep' })
    }
  }
  for (const relation of relations.filter(item => item.resolution === 'resolved')) {
    if (!visible.some(item => item.ref === relation.review_occurrence_ref && item.run_ref === relation.source_run_ref)) continue
    // One declared link enters the first actual fixing call; later calls remain distinct.
    const fix = visible.filter(item => item.run_ref === relation.run_ref && item.role === 'fixing_worker').sort((a, b) => seq(a) - seq(b))[0]
    if (fix) edges.push({ id: `followup_${relation.review_occurrence_ref}_${fix.ref}`, source: relation.review_occurrence_ref, target: fix.ref, label: 'Declared correction', type: 'smoothstep' })
  }
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.id, edge.source, edge.target]).sort() }) }
}
export function recordText(record: Observation) {
  return [`${record.kind}; sequence ${record.source_seq}`, record.recorded_at != null ? `recorded ${record.recorded_at}` : 'recorded time unknown', record.ordinal != null ? `check ${record.ordinal}` : '', record.exit_code != null ? `exit ${record.exit_code}` : '', record.approved != null ? `approved ${record.approved}` : '', record.finding_count != null ? `findings ${record.finding_count}` : '', record.no_change != null ? `no change ${record.no_change}` : '', record.baseline ? `baseline ${record.baseline}` : '', record.head ? `head ${record.head}` : '', record.review_base && record.review_head ? `range ${record.review_base} → ${record.review_head}` : '', `record ${record.ref}`].filter(Boolean).join('; ')
}
