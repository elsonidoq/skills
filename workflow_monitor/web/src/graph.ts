import type { Edge, Node } from '@xyflow/react'
export type Observation = { ref: string; run_ref: string; occurrence_ref: string; kind: string; source_seq: number; recorded_at: number | null; parent_occurrence_id?: string; error_category?: string | null; recording_gap?: boolean; ordinal?: number | null; exit_code: number | null; finding_count: number | null; approved?: boolean | null; no_change?: boolean | null; baseline?: string | null; head?: string | null; review_base: string | null; review_head: string | null }
export type GraphEdge = { ref: string; run_ref: string; type: string; from_ref: string; to_ref: string; resolution: string }
export type ChainExecution = { ref: string; run_ref: string; execution_id: string; role: 'reviewer' | 'fixer' | 'unknown'; review_ordinal: number | null; fixing_round: number | null; outcome: 'approved' | 'rejected' | 'failed' | 'interrupted' | 'unknown'; trigger_ref: string | null; predecessor_ref: string | null; occurrence_refs: string[]; review_range: { base: string | null; head: string | null }; findings: string[]; commit_refs: Record<string, string> }
export type ExecutionSummary = { state: 'success' | 'failure' | 'waiting' | 'running' | 'unknown'; qualification: string | null }
export type Occurrence = { ref: string; run_ref: string; occurrence_id?: string; phase_ref: string; task_ref: string | null; role: string; outcome: string | null; completeness: string; record_refs: string[]; phase?: string; first_seq?: number; last_seq?: number; parent_ref?: string | null; support_ref?: string | null; stopping?: boolean; execution_summary?: ExecutionSummary }
export type PlannedTask = { ref: string; run_ref: string; task_id?: string; label: string; summary: string; prerequisite_refs: string[]; progress?: { state: string; qualification: string | null }; reason?: { code: string; occurrence_ref?: string; task_ref?: string } | null; annotation?: { code?: string; label?: string; occurrence_ref?: string } | null }
export type ReviewDefinition = { ref: string; run_ref: string; label: string }
export type GraphSnapshot = { runs: Array<{ ref: string; plan_availability?: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; edges?: GraphEdge[]; chain?: ChainExecution[] }
export type Followup = { run_ref: string; source_run_ref: string; review_occurrence_ref: string; resolution: string }
export function action(item: Occurrence, snapshots: GraphSnapshot[]) {
  const verb = item.role === 'worker' ? 'Implement' : item.role === 'fixing_worker' ? 'Fix' : item.role === 'reviewer' ? 'Review' : ({ check: 'Check', checkpoint: 'Checkpoint', prepare: 'Prepare', gate: 'Gate', terminal: 'Stop' }[item.phase ?? ''] ?? 'Stop')
  const task = snapshots.flatMap(snapshot => snapshot.tasks).find(task => task.ref === item.task_ref && task.run_ref === item.run_ref)
  return `${verb}${task ? ` ${task.label.length > 24 ? task.label.slice(0, 23) + '…' : task.label}` : ''}`
}
export function status(item: Occurrence, records: Observation[]) {
  if (item.execution_summary) return item.execution_summary.state === 'failure' ? 'failed' : item.execution_summary.state === 'success' ? 'success' : item.execution_summary.state
  const own = records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref)
  if (item.outcome === 'failed' || own.some(record => record.kind === 'failed' || record.kind === 'delivery_failed')) return 'failed'
  if (item.outcome === 'passed') return 'success'
  const allOwnRecordsLoaded = item.record_refs.every(ref => own.some(record => record.ref === ref))
  if (allOwnRecordsLoaded && own.some(record => record.kind === 'question_requested') && !own.some(record => record.kind === 'answer_sent' || record.kind === 'answer_returned')) return 'waiting'
  return 'neutral'
}
export function outcomeText(item: Occurrence, records: Observation[]) {
  if (item.execution_summary) return item.execution_summary.state === 'success' ? 'returned — acceptance not established' : item.execution_summary.state === 'failure' ? 'failed' : `${item.execution_summary.state} — ${item.execution_summary.qualification ?? 'recorded qualification'}`
  if (item.outcome) return item.outcome
  const own = records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref)
  if (own.some(record => record.kind === 'returned')) return 'returned — acceptance not established'
  return item.completeness === 'incomplete' ? 'incomplete — outcome unknown' : 'recorded — outcome unknown'
}
const seq = (item: Occurrence, records: Observation[]) => item.first_seq ?? Math.min(...records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref).map(record => record.source_seq), Number.MAX_SAFE_INTEGER)
export function graphFor(root: GraphSnapshot, lineage: GraphSnapshot[], relations: Followup[]) {
  const snapshots = [root, ...lineage], occurrences = snapshots.flatMap(item => item.occurrences), records = snapshots.flatMap(item => item.records), chain = snapshots.flatMap(item => item.chain ?? []), recordedEdges = snapshots.flatMap(item => item.edges ?? [])
  const planAvailable = root.runs.some(run => run.plan_availability === 'complete')
  const planned = planAvailable ? root.tasks : []
  const planRuns = new Set(planned.map(task => task.run_ref))
  const reviews = planAvailable ? (root.review_definitions ?? []).filter(review => planRuns.has(review.run_ref)) : []
  const chainOccurrences = new Set(chain.flatMap(item => item.occurrence_refs))
  const chainSupport = new Set(recordedEdges.filter(edge => edge.type === 'chain_check' || edge.type === 'chain_checkpoint').flatMap(edge => [edge.from_ref, edge.to_ref]))
  const visible = occurrences.filter(item => (!chainOccurrences.has(item.ref) && ['worker', 'fixing_worker', 'reviewer'].includes(item.role)) || chainSupport.has(item.ref) || item.stopping)
  const nodes: Node[] = [
    ...planned.map(task => ({ id: task.ref, position: { x: 0, y: 0 }, data: { label: task.label, status: `Plan progress: ${task.progress?.state ?? 'pending'}${task.annotation?.label ? ` — ${task.annotation.label}` : ''}` }, className: `planned-node progress-${task.progress?.state ?? 'pending'}` })),
    ...reviews.map(review => ({ id: review.ref, position: { x: 0, y: 0 }, data: { label: review.label, status: 'Declared stage' }, className: 'planned-review-node' })),
    ...visible.map(item => {
      const ownStatus = status(item, records)
      const color = item.stopping ? 'failed' : ownStatus === 'neutral' && occurrences.some(child => child.run_ref === item.run_ref && child.parent_ref === item.ref && status(child, records) === 'waiting') ? 'waiting' : ownStatus
      const support = recordedEdges.find(edge => edge.to_ref === item.ref && (edge.type === 'chain_check' || edge.type === 'chain_checkpoint'))
      const task = snapshots.flatMap(snapshot => snapshot.tasks).find(candidate => candidate.ref === item.task_ref)
      const label = support ? `${support.type === 'chain_check' ? 'Check' : 'Checkpoint'}${task ? ` ${task.label}` : ''}` : action(item, snapshots)
      return { id: item.ref, position: { x: 0, y: 0 }, data: { label, status: color === 'waiting' ? 'waiting — recorded question' : outcomeText(item, records) }, className: `execution-node ${color}` }
    }),
    ...chain.map(item => {
      const failed = item.outcome === 'failed' || item.outcome === 'interrupted'
      const label = item.role === 'fixer' ? 'Fixing agent' : item.role === 'reviewer' ? `Review ${item.review_ordinal ?? 'unknown'}` : 'Recorded execution'
      const outcome = item.outcome === 'rejected' ? `rejected${item.findings.length ? ` — ${item.findings.length} finding${item.findings.length === 1 ? '' : 's'}` : ''}` : item.outcome
      return { id: item.ref, position: { x: 0, y: 0 }, data: { label, status: outcome }, className: `execution-node chain-node ${failed ? 'failed' : item.outcome === 'unknown' ? 'neutral' : 'success'}` }
    })
  ]
  const edges: Edge[] = []
  for (const task of planned) for (const prerequisite of task.prerequisite_refs) edges.push({ id: `dependency_${prerequisite}_${task.ref}`, source: prerequisite, target: task.ref, label: 'Declared prerequisite', type: 'smoothstep', className: 'dependency-edge' })
  for (const item of visible.filter(item => !chainSupport.has(item.ref))) {
    const parent = item.role === 'reviewer' ? reviews.find(review => review.run_ref === item.run_ref) : planned.find(task => task.ref === item.task_ref)
    if (parent) edges.push({ id: `attachment_${parent.ref}_${item.ref}`, source: parent.ref, target: item.ref, label: 'Recorded attachment', type: 'smoothstep', className: 'attachment-edge' })
  }
  for (const run of new Set(visible.map(item => item.run_ref))) {
    const agents = visible.filter(item => item.run_ref === run && item.role !== 'non_model' && !chainOccurrences.has(item.ref)).sort((a, b) => seq(a, records) - seq(b, records))
    for (let index = 1; index < agents.length; index++) edges.push({ id: `sequence_${agents[index - 1].ref}_${agents[index].ref}`, source: agents[index - 1].ref, target: agents[index].ref, label: 'Recorded sequence', type: 'smoothstep', className: 'sequence-edge' })
    for (const stop of visible.filter(item => item.run_ref === run && item.stopping)) {
      const parent = agents.find(item => item.ref === stop.support_ref)
      if (parent) edges.push({ id: `stop_${stop.ref}`, source: parent.ref, target: stop.ref, label: 'Stopping step', type: 'smoothstep' })
    }
  }
  for (const edge of recordedEdges.filter(edge => edge.type.startsWith('chain_') && nodes.some(node => node.id === edge.from_ref) && nodes.some(node => node.id === edge.to_ref))) {
    const label = edge.type === 'chain_trigger' ? 'Recorded trigger' : edge.type === 'chain_predecessor' ? 'Recorded predecessor' : edge.type === 'chain_check' ? 'Fixer check' : 'Fixer checkpoint'
    edges.push({ id: edge.ref, source: edge.from_ref, target: edge.to_ref, label, type: 'smoothstep', className: 'chain-edge' })
  }
  for (const relation of relations.filter(item => item.resolution === 'resolved')) {
    if (!visible.some(item => item.ref === relation.review_occurrence_ref && item.run_ref === relation.source_run_ref)) continue
    const fix = visible.filter(item => item.run_ref === relation.run_ref && item.role === 'fixing_worker').sort((a, b) => seq(a, records) - seq(b, records))[0]
    if (fix) edges.push({ id: `followup_${relation.review_occurrence_ref}_${fix.ref}`, source: relation.review_occurrence_ref, target: fix.ref, label: 'Declared correction', type: 'smoothstep', className: 'correction-edge' })
  }
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.id, edge.source, edge.target]).sort() }) }
}
export function recordText(record: Observation) {
  return [`${record.kind}; sequence ${record.source_seq}`, record.recorded_at != null ? `recorded ${record.recorded_at}` : 'recorded time unknown', record.ordinal != null ? `check ${record.ordinal}` : '', record.exit_code != null ? `exit ${record.exit_code}` : '', record.approved != null ? `approved ${record.approved}` : '', record.finding_count != null ? `findings ${record.finding_count}` : '', record.no_change != null ? `no change ${record.no_change}` : '', record.baseline ? `baseline ${record.baseline}` : '', record.head ? `head ${record.head}` : '', record.review_base && record.review_head ? `range ${record.review_base} → ${record.review_head}` : '', record.parent_occurrence_id ? `parent ${record.parent_occurrence_id}` : '', record.error_category ? `error ${record.error_category}` : '', record.recording_gap ? 'recording gap' : '', `record ${record.ref}`].filter(Boolean).join('; ')
}
