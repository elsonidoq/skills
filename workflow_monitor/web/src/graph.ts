import type { Edge, Node } from '@xyflow/react'

export type Observation = { ref: string; run_ref: string; occurrence_ref: string; kind: string; source_seq: number; recorded_at: number | null; parent_occurrence_id?: string; error_category?: string | null; recording_gap?: boolean; ordinal?: number | null; exit_code: number | null; finding_count: number | null; approved?: boolean | null; no_change?: boolean | null; baseline?: string | null; head?: string | null; review_base: string | null; review_head: string | null }
export type GraphEdge = { ref: string; run_ref: string; type: string; from_ref: string; to_ref: string; resolution: string }
export type ChainExecution = { ref: string; run_ref: string; execution_id: string; role: 'reviewer' | 'fixer' | 'unknown'; review_ordinal: number | null; fixing_round: number | null; outcome: 'approved' | 'rejected' | 'failed' | 'interrupted' | 'unknown'; trigger_ref: string | null; predecessor_ref: string | null; input_refs: string[]; occurrence_refs: string[]; review_range: { base: string | null; head: string | null }; findings: string[]; commit_refs: Record<string, string> }
export type Activity = { ref: string; run_ref: string; invocation_id: string; occurrence_ref: string; task_ref: string | null; role: 'worker' | 'fixing_worker' | 'reviewer' | 'unknown'; invocation_kind: 'task_worker' | 'corrective_worker' | 'unknown'; outcome: 'returned' | 'failed' | 'interrupted' | 'unknown'; error_category: string | null; input_qualification: 'recorded' | 'unknown'; input_refs: string[]; correction_chain: string[]; support_ref: string | null; stopped_by_ref: string | null; record_refs: string[]; metrics?: unknown; task_metrics?: unknown; trigger_ref?: string | null }
export type ExecutionSummary = { state: 'success' | 'failure' | 'waiting' | 'running' | 'unknown'; qualification: string | null }
export type Occurrence = { ref: string; run_ref: string; occurrence_id?: string; phase_ref: string; task_ref: string | null; role: string; outcome: string | null; completeness: string; record_refs: string[]; phase?: string; first_seq?: number; last_seq?: number; parent_ref?: string | null; support_ref?: string | null; stopping?: boolean; execution_summary?: ExecutionSummary }
export type PlannedTask = { ref: string; run_ref: string; task_id?: string; label: string; summary: string; prerequisite_refs: string[]; progress?: { state: string; qualification: string | null }; reason?: { code: string; occurrence_ref?: string; task_ref?: string } | null; annotation?: { code?: string; label?: string; occurrence_ref?: string } | null }
export type ReviewDefinition = { ref: string; run_ref: string; label: string }
export type GraphSnapshot = { runs: Array<{ ref: string; plan_availability?: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; edges?: GraphEdge[]; chain?: ChainExecution[]; activities?: Activity[] }
export type Followup = { run_ref: string; source_run_ref: string; review_occurrence_ref: string; resolution: string }

const genericTitle = (value: string | undefined, taskId?: string) => !value || /^task(?:\s|$)/i.test(value.trim()) || (taskId != null && value.trim() === taskId)
export function taskTitle(task: PlannedTask) {
  const summary = task.summary.trim()
  const title = genericTitle(task.label, task.task_id) && summary ? summary : task.label || summary || 'Unknown task title'
  return title.length > 80 ? `${title.slice(0, 79)}…` : title
}
const roleName = (role: string) => role === 'worker' ? 'Worker' : role === 'fixing_worker' ? 'Corrective worker' : role === 'reviewer' ? 'Reviewer' : role === 'fixer' ? 'Fixing worker' : 'Stop'
export function action(item: Occurrence, snapshots: GraphSnapshot[]) {
  const task = snapshots.flatMap(snapshot => snapshot.tasks).find(candidate => candidate.ref === item.task_ref && candidate.run_ref === item.run_ref)
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

/** Project only recorded calls and explicit relations; plans and observation sequence are details. */
export function graphFor(root: GraphSnapshot, lineage: GraphSnapshot[], _relations: Followup[]) {
  const snapshots = [root, ...lineage]
  const occurrences = snapshots.flatMap(snapshot => snapshot.occurrences)
  const activities = snapshots.flatMap(snapshot => snapshot.activities ?? [])
  const chain = snapshots.flatMap(snapshot => snapshot.chain ?? [])
  const tasks = snapshots.flatMap(snapshot => snapshot.tasks)
  const key = (runRef: string, ref: string) => `${runRef}\u0000${ref}`
  const taskFor = (activity: Activity) => activity.task_ref ? tasks.find(task => task.ref === activity.task_ref && task.run_ref === activity.run_ref) : undefined

  // A chain execution may stand in for an occurrence only when it names that one
  // occurrence and no competing chain names it. Shared membership (OI-16) remains
  // visible as its own activity/stop instead of assigning it by metadata.
  const memberships = new Map<string, string[]>()
  for (const execution of chain) for (const occurrence of execution.occurrence_refs) {
    const membershipKey = key(execution.run_ref, occurrence)
    memberships.set(membershipKey, [...(memberships.get(membershipKey) ?? []), execution.ref])
  }
  const alias = new Map([...memberships].flatMap(([membershipKey, refs]) => {
    const execution = refs.length === 1 ? chain.find(item => item.ref === refs[0]) : undefined
    // A fixing execution can retain several distinct corrective calls.  It is
    // not an invocation alias unless its membership is exactly one occurrence.
    return execution?.occurrence_refs.length === 1 ? [[membershipKey, refs[0]] as const] : []
  }))
  const nodeForOccurrence = (runRef: string, occurrenceRef: string) => alias.get(key(runRef, occurrenceRef)) ?? activities.find(activity => activity.run_ref === runRef && activity.occurrence_ref === occurrenceRef)?.ref ?? occurrenceRef
  const activityNodes = activities.filter(activity => !alias.has(key(activity.run_ref, activity.occurrence_ref))).map(activity => {
    const task = taskFor(activity)
    const title = `${roleName(activity.role)}${task ? ` — ${taskTitle(task)}` : ''}${activity.invocation_kind === 'corrective_worker' ? ' (correction)' : ''}`
    const outcome = activity.outcome === 'returned' ? 'returned — acceptance not established' : activity.outcome
    return { id: activity.ref, position: { x: 0, y: 0 }, data: { label: title, status: `${outcome}${activity.error_category ? ` — ${activity.error_category}` : ''}`, identity: { ref: activity.ref, runRef: activity.run_ref, invocationId: activity.invocation_id, taskId: task?.task_id ?? null }, relationQualification: activity.input_qualification === 'recorded' ? null : 'Input relations unknown/not recorded.' }, className: `execution-node actual-call ${activity.outcome === 'failed' ? 'failed' : activity.outcome === 'unknown' ? 'neutral' : 'success'}` } satisfies Node
  })
  // A fixing round is not another call. Multiple retained prompt occurrences
  // are already represented by their distinct activities; do not invent a
  // round-to-invocation endpoint for its aggregate relations.
  const chainNodes = chain.filter(execution => execution.role !== 'fixer' || execution.occurrence_refs.length === 1).map(execution => {
    const title = execution.role === 'reviewer' ? `Review ${execution.review_ordinal ?? 'unknown'}` : execution.role === 'fixer' ? `Fixing worker${execution.fixing_round == null ? '' : ` round ${execution.fixing_round}`}` : 'Recorded execution'
    return { id: execution.ref, position: { x: 0, y: 0 }, data: { label: title, status: execution.outcome, identity: { ref: execution.ref, runRef: execution.run_ref, executionId: execution.execution_id, occurrenceRefs: execution.occurrence_refs } }, className: `execution-node chain-node actual-call ${execution.outcome === 'failed' || execution.outcome === 'interrupted' ? 'failed' : execution.outcome === 'unknown' ? 'neutral' : 'success'}` } satisfies Node
  })
  const stopNodes = occurrences.filter(occurrence => occurrence.stopping && !activities.some(activity => activity.run_ref === occurrence.run_ref && activity.occurrence_ref === occurrence.ref) && !alias.has(key(occurrence.run_ref, occurrence.ref))).map(occurrence => ({ id: occurrence.ref, position: { x: 0, y: 0 }, data: { label: 'Execution stopped', status: occurrence.outcome ?? 'cause unknown', identity: { ref: occurrence.ref, runRef: occurrence.run_ref, occurrenceId: occurrence.occurrence_id ?? null }, relationQualification: occurrence.support_ref ? null : 'Stopping cause unknown.' }, className: 'execution-node stop-node failed' } satisfies Node))
  const nodes: Node[] = [...activityNodes, ...chainNodes, ...stopNodes]
  const nodeExists = (id: string) => nodes.some(node => node.id === id)
  const edges: Edge[] = []
  const edgeByPair = new Map<string, Edge>()
  const rejected = new Map<string, string[]>()
  const reject = (node: string, reason: string) => rejected.set(node, [...(rejected.get(node) ?? []), reason])
  const reaches = (from: string, target: string, seen = new Set<string>()): boolean => {
    if (from === target) return true
    if (seen.has(from)) return false
    seen.add(from)
    return edges.some(edge => edge.source === from && reaches(edge.target, target, seen))
  }
  const add = (id: string, source: string, target: string, relation: string, identity: Record<string, unknown>) => {
    if (source === target) { reject(target, `${relation}: self relation rejected.`); return }
    if (!nodeExists(source) || !nodeExists(target)) { reject(target, `${relation}: endpoint missing or ambiguous.`); return }
    const pair = `${source}\u0000${target}`
    const existing = edgeByPair.get(pair)
    if (existing) {
      const data = existing.data as { relations: string[]; identities: Record<string, unknown>[] }
      if (!data.relations.includes(relation)) { data.relations.push(relation); data.identities.push(identity) }
      return
    }
    if (reaches(target, source)) { reject(target, `${relation}: cyclic relation rejected.`); return }
    const edge: Edge = { id, source, target, type: 'smoothstep', className: 'secondary-edge actual-edge', data: { classification: 'actual', relation, relations: [relation], resolution: 'recorded', identity, identities: [identity] } }
    edgeByPair.set(pair, edge); edges.push(edge)
  }
  for (const activity of activities) {
    if (!nodeExists(activity.ref)) continue
    if (activity.trigger_ref) add(`trigger_${activity.trigger_ref}_${activity.ref}`, activity.trigger_ref, activity.ref, 'recorded-correction-trigger', { triggerRef: activity.trigger_ref, correctionRef: activity.ref })
    if (activity.input_qualification === 'recorded') for (const input of activity.input_refs) add(`input_${input}_${activity.ref}`, input, activity.ref, 'recorded-input', { producerRef: input, consumerRef: activity.ref })
    for (const predecessor of activity.correction_chain.filter(ref => ref !== activity.ref)) add(`correction_${predecessor}_${activity.ref}`, predecessor, activity.ref, 'recorded-correction', { predecessorRef: predecessor, correctionRef: activity.ref })
  }
  for (const execution of chain) {
    for (const input of execution.input_refs ?? []) add(`review_input_${input}_${execution.ref}`, input, execution.ref, 'recorded-review-input', { producerRef: input, reviewRef: execution.ref })
    if (execution.trigger_ref) add(`trigger_${execution.trigger_ref}_${execution.ref}`, execution.trigger_ref, execution.ref, 'recorded-correction-trigger', { triggerRef: execution.trigger_ref, executionRef: execution.ref })
    if (execution.predecessor_ref) add(`predecessor_${execution.predecessor_ref}_${execution.ref}`, execution.predecessor_ref, execution.ref, 'recorded-correction-predecessor', { predecessorRef: execution.predecessor_ref, executionRef: execution.ref })
  }
  for (const stop of occurrences.filter(occurrence => occurrence.stopping && occurrence.support_ref)) {
    const source = nodeForOccurrence(stop.run_ref, stop.support_ref!), target = nodeForOccurrence(stop.run_ref, stop.ref)
    add(`stop_${stop.ref}`, source, target, 'recorded-stop-support', { supportRef: stop.support_ref, stopRef: stop.ref, runRef: stop.run_ref })
  }
  for (const node of nodes) {
    const qualifications = rejected.get(node.id)
    if (qualifications?.length) node.data = { ...node.data, relationQualification: qualifications.join(' ') }
  }
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.source, edge.target, edge.data?.relation]).sort() }) }
}
export function recordText(record: Observation) {
  return [`${record.kind}; sequence ${record.source_seq}`, record.recorded_at != null ? `recorded ${record.recorded_at}` : 'recorded time unknown', record.ordinal != null ? `check ${record.ordinal}` : '', record.exit_code != null ? `exit ${record.exit_code}` : '', record.approved != null ? `approved ${record.approved}` : '', record.finding_count != null ? `findings ${record.finding_count}` : '', record.no_change != null ? `no change ${record.no_change}` : '', record.baseline ? `baseline ${record.baseline}` : '', record.head ? `head ${record.head}` : '', record.review_base && record.review_head ? `range ${record.review_base} → ${record.review_head}` : '', record.parent_occurrence_id ? `parent ${record.parent_occurrence_id}` : '', record.error_category ? `error ${record.error_category}` : '', record.recording_gap ? 'recording gap' : '', `record ${record.ref}`].filter(Boolean).join('; ')
}
