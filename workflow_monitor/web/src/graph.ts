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
const genericTitle = (value: string | undefined, taskId?: string) => !value || /^task(?:\s|$)/i.test(value.trim()) || (taskId != null && value.trim() === taskId)
export function taskTitle(task: PlannedTask) {
  const summary = task.summary.trim()
  const title = genericTitle(task.label, task.task_id) && summary ? summary : task.label || summary || 'Unknown task title'
  return title.length > 80 ? `${title.slice(0, 79)}…` : title
}
function taskCode(task: PlannedTask) {
  return task.task_id?.trim() || 'Unknown task ID'
}
const roleName = (role: string) => role === 'worker' ? 'Worker' : role === 'fixing_worker' ? 'Fixing worker' : role === 'reviewer' ? 'Reviewer' : ({ check: 'Check', checkpoint: 'Checkpoint', prepare: 'Prepare', gate: 'Gate', terminal: 'Stop' }[role] ?? 'Recorded occurrence')
export function action(item: Occurrence, snapshots: GraphSnapshot[]) {
  const task = snapshots.flatMap(snapshot => snapshot.tasks).find(task => task.ref === item.task_ref && task.run_ref === item.run_ref)
  return `${roleName(item.role)}${task ? ` — ${taskTitle(task)}` : ''}`
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
export function graphFor(root: GraphSnapshot, lineage: GraphSnapshot[], relations: Followup[]) {
  const snapshots = [root, ...lineage], occurrences = snapshots.flatMap(item => item.occurrences), records = snapshots.flatMap(item => item.records), chain = snapshots.flatMap(item => item.chain ?? []), rawEdges = snapshots.flatMap(item => item.edges ?? [])
  // Producer chain support edges reference observations, not occurrence nodes.
  // Resolve via explicit record membership, including records outside this page.
  const recordedEdges = rawEdges.map(edge => {
    if (edge.type !== 'chain_check' && edge.type !== 'chain_checkpoint') return edge
    const target = occurrences.find(item => item.run_ref === edge.run_ref &&
      (item.ref === edge.to_ref || item.record_refs.includes(edge.to_ref)))
    return target ? { ...edge, to_ref: target.ref } : edge
  })
  const planAvailable = root.runs.some(run => run.plan_availability === 'complete')
  const planned = planAvailable ? root.tasks : []
  const planRuns = new Set(planned.map(task => task.run_ref))
  const reviews = planAvailable ? (root.review_definitions ?? []).filter(review => planRuns.has(review.run_ref)) : []
  const occurrenceKey = (runRef: string, ref: string) => `${runRef}\u0000${ref}`
  const chainByOccurrence = new Map<string, string[]>()
  for (const execution of chain) for (const ref of execution.occurrence_refs) {
    const key = occurrenceKey(execution.run_ref, ref)
    chainByOccurrence.set(key, [...(chainByOccurrence.get(key) ?? []), execution.ref])
  }
  // An occurrence is replaced only by its single recorded same-run execution. Ambiguous
  // membership remains an occurrence rather than guessing which execution owns it.
  const representedByChain = new Map([...chainByOccurrence].flatMap(([key, refs]) => refs.length === 1 ? [[key, refs[0]] as const] : []))
  const chainOccurrences = new Set(chainByOccurrence.keys())
  const nodeRefFor = (runRef: string, ref: string) => representedByChain.get(occurrenceKey(runRef, ref)) ?? ref
  const visible = occurrences.filter(item => !chainOccurrences.has(occurrenceKey(item.run_ref, item.ref)) &&
    (['worker', 'fixing_worker', 'reviewer'].includes(item.role) || item.stopping || recordedEdges.some(edge =>
      (edge.type === 'chain_check' || edge.type === 'chain_checkpoint') && edge.run_ref === item.run_ref && (edge.from_ref === item.ref || edge.to_ref === item.ref)) ||
      occurrences.some(stop => stop.stopping && stop.run_ref === item.run_ref && stop.support_ref === item.ref)))
  const plannedByRef = new Map(planned.map(task => [task.ref, task]))
  const occurrenceOwner = (item: Occurrence) => item.task_ref && plannedByRef.get(item.task_ref)?.run_ref === item.run_ref ? item.task_ref : null
  const attemptLabel = (item: Occurrence) => `${roleName(item.role)} attempt ${item.occurrence_id ?? 'unknown'}`
  const nodes: Node[] = [
    ...planned.map(task => ({ id: task.ref, position: { x: 0, y: 0 }, data: { label: taskTitle(task), taskCode: taskCode(task), title: taskTitle(task), status: `Plan progress: ${task.progress?.state ?? 'pending'}${task.annotation?.label ? ` — ${task.annotation.label}` : ''}`, identity: { ref: task.ref, runRef: task.run_ref, taskId: task.task_id ?? null } }, className: `planned-node progress-${task.progress?.state ?? 'pending'}` })),
    ...reviews.map(review => ({ id: review.ref, position: { x: 0, y: 0 }, data: { label: review.label, status: 'Declared stage', identity: { ref: review.ref, runRef: review.run_ref, kind: 'planned-review-definition' }, owner: null }, className: 'planned-review-node' })),
    ...visible.map(item => {
      const ownStatus = status(item, records)
      const color = item.stopping ? 'failed' : ownStatus === 'neutral' && occurrences.some(child => child.run_ref === item.run_ref && child.parent_ref === item.ref && status(child, records) === 'waiting') ? 'waiting' : ownStatus
      const support = recordedEdges.find(edge => edge.to_ref === item.ref && (edge.type === 'chain_check' || edge.type === 'chain_checkpoint'))
      const owner = occurrenceOwner(item)
      const label = support ? `${support.type === 'chain_check' ? 'Check' : 'Checkpoint'} — ${attemptLabel(item)}` : `${attemptLabel(item)}${owner ? ` — ${taskTitle(plannedByRef.get(owner)!)}` : ''}`
      return { id: item.ref, position: { x: 0, y: 0 }, data: { label, status: color === 'waiting' ? 'waiting — recorded question' : outcomeText(item, records), identity: { ref: item.ref, runRef: item.run_ref, occurrenceId: item.occurrence_id ?? null }, owner: owner ?? { scope: 'run', runRef: item.run_ref, state: 'unassigned' } }, className: `execution-node ${color}` }
    }),
    ...chain.map(item => {
      const members = occurrences.filter(occurrence => item.occurrence_refs.includes(occurrence.ref) && occurrence.run_ref === item.run_ref).map(occurrenceOwner).filter((owner): owner is string => owner != null)
      const owners = [...new Set(members)]
      const owner = owners.length === 1 && members.length === item.occurrence_refs.length ? owners[0] : null
      const failed = item.outcome === 'failed' || item.outcome === 'interrupted'
      const label = item.role === 'fixer' ? `Fixing agent${item.fixing_round != null ? ` round ${item.fixing_round}` : ''}` : item.role === 'reviewer' ? `Review ${item.review_ordinal ?? 'unknown'}` : 'Recorded execution'
      const outcome = item.outcome === 'rejected' ? `rejected${item.findings.length ? ` — ${item.findings.length} finding${item.findings.length === 1 ? '' : 's'}` : ''}` : item.outcome
      return { id: item.ref, position: { x: 0, y: 0 }, data: { label, status: outcome, identity: { ref: item.ref, runRef: item.run_ref, executionId: item.execution_id, occurrenceRefs: item.occurrence_refs }, owner: owner ?? { scope: 'run', runRef: item.run_ref, state: 'unassigned' } }, className: `execution-node chain-node ${failed ? 'failed' : item.outcome === 'unknown' ? 'neutral' : 'success'}` }
    })
  ]
  const edges: Edge[] = []
  const nodeFor = (runRef: string, ref: string) => nodes.some(node => node.id === nodeRefFor(runRef, ref) && (node.data.identity as { runRef?: string } | undefined)?.runRef === runRef)
  for (const task of planned) for (const prerequisite of task.prerequisite_refs) edges.push({ id: `dependency_${prerequisite}_${task.ref}`, source: prerequisite, target: task.ref, type: 'smoothstep', className: 'dependency-edge', data: { classification: 'backbone', relation: 'declared-prerequisite', identity: { prerequisiteRef: prerequisite, dependentRef: task.ref, runRef: task.run_ref } } })
  for (const stop of occurrences.filter(item => item.stopping && item.support_ref != null && nodeFor(item.run_ref, item.support_ref!) && nodeFor(item.run_ref, item.ref))) {
    const source = nodeRefFor(stop.run_ref, stop.support_ref!), target = nodeRefFor(stop.run_ref, stop.ref)
    edges.push({ id: `stop_${stop.ref}`, source, target, type: 'smoothstep', className: 'secondary-edge stop-edge', data: { classification: 'secondary', relation: 'recorded-stop-support', resolution: 'recorded', identity: { runRef: stop.run_ref, supportRef: stop.support_ref, stopRef: stop.ref } } })
  }
  for (const edge of recordedEdges.filter(edge => edge.type.startsWith('chain_') && nodeFor(edge.run_ref, edge.from_ref) && nodeFor(edge.run_ref, edge.to_ref))) {
    const source = nodeRefFor(edge.run_ref, edge.from_ref), target = nodeRefFor(edge.run_ref, edge.to_ref)
    edges.push({ id: edge.ref, source, target, type: 'smoothstep', className: 'secondary-edge chain-edge', data: { classification: 'secondary', relation: edge.type, resolution: edge.resolution, identity: { ref: edge.ref, runRef: edge.run_ref, fromRef: edge.from_ref, toRef: edge.to_ref } } })
  }
  for (const relation of relations.filter(item => item.resolution === 'resolved' && nodeFor(item.source_run_ref, item.review_occurrence_ref))) {
    const fixes = [
      ...visible.filter(item => item.run_ref === relation.run_ref && item.role === 'fixing_worker').map(item => item.ref),
      ...chain.filter(item => item.run_ref === relation.run_ref && item.role === 'fixer').map(item => item.ref)
    ]
    const source = nodeRefFor(relation.source_run_ref, relation.review_occurrence_ref)
    for (const fix of new Set(fixes)) edges.push({ id: `followup_${relation.review_occurrence_ref}_${fix}`, source, target: fix, type: 'smoothstep', className: 'secondary-edge correction-edge', data: { classification: 'secondary', relation: 'declared-cross-run-correction', resolution: relation.resolution, qualification: 'declared cross-run correction; not recorded exact execution causality', identity: { sourceRunRef: relation.source_run_ref, reviewOccurrenceRef: relation.review_occurrence_ref, correctionRunRef: relation.run_ref, fixingRef: fix } } })
  }
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.id, edge.source, edge.target]).sort() }) }
}
export function recordText(record: Observation) {
  return [`${record.kind}; sequence ${record.source_seq}`, record.recorded_at != null ? `recorded ${record.recorded_at}` : 'recorded time unknown', record.ordinal != null ? `check ${record.ordinal}` : '', record.exit_code != null ? `exit ${record.exit_code}` : '', record.approved != null ? `approved ${record.approved}` : '', record.finding_count != null ? `findings ${record.finding_count}` : '', record.no_change != null ? `no change ${record.no_change}` : '', record.baseline ? `baseline ${record.baseline}` : '', record.head ? `head ${record.head}` : '', record.review_base && record.review_head ? `range ${record.review_base} → ${record.review_head}` : '', record.parent_occurrence_id ? `parent ${record.parent_occurrence_id}` : '', record.error_category ? `error ${record.error_category}` : '', record.recording_gap ? 'recording gap' : '', `record ${record.ref}`].filter(Boolean).join('; ')
}
