import type { Edge, Node } from '@xyflow/react'

export type Observation = { ref: string; run_ref: string; occurrence_ref: string; kind: string; source_seq: number; recorded_at: number | null; parent_occurrence_id?: string; error_category?: string | null; recording_gap?: boolean; ordinal?: number | null; exit_code: number | null; finding_count: number | null; approved?: boolean | null; no_change?: boolean | null; baseline?: string | null; head?: string | null; review_base: string | null; review_head: string | null }
export type GraphEdge = { ref: string; run_ref: string; type: string; from_ref: string; to_ref: string; resolution: string }
export type ChainExecution = { ref: string; run_ref: string; execution_id: string; role: 'reviewer' | 'fixer' | 'unknown'; review_ordinal: number | null; fixing_round: number | null; outcome: 'approved' | 'rejected' | 'failed' | 'interrupted' | 'unknown'; trigger_ref: string | null; predecessor_ref: string | null; input_refs: string[]; occurrence_refs: string[]; review_range: { base: string | null; head: string | null }; findings: string[]; attempts?: Array<{ outcome: string; uncertain: boolean; findings: string[] }>; commit_refs: Record<string, string> }
export type Activity = { ref: string; run_ref: string; invocation_id: string; occurrence_ref: string | null; task_ref: string | null; role: 'worker' | 'fixing_worker' | 'reviewer' | 'unknown'; invocation_kind: 'task_worker' | 'corrective_worker' | 'unknown'; outcome: 'returned' | 'failed' | 'interrupted' | 'unknown'; error_category: string | null; input_qualification: 'recorded' | 'unknown'; input_refs: string[]; correction_chain: string[]; support_ref: string | null; stopped_by_ref: string | null; record_refs: string[]; metrics?: unknown; task_metrics?: unknown; trigger_ref?: string | null }
export type ExecutionSummary = { state: 'success' | 'failure' | 'waiting' | 'running' | 'unknown'; qualification: string | null }
export type Occurrence = { ref: string; run_ref: string; occurrence_id?: string; phase_ref: string; task_ref: string | null; role: string; outcome: string | null; completeness: string; record_refs: string[]; phase?: string; first_seq?: number; last_seq?: number; parent_ref?: string | null; support_ref?: string | null; stopping?: boolean; execution_summary?: ExecutionSummary }
export type PlannedTask = { ref: string; run_ref: string; task_id?: string; label: string; work_description?: string | null; prerequisite_refs: string[]; progress?: { state: string; qualification: string | null }; reason?: { code: string; occurrence_ref?: string; task_ref?: string } | null; annotation?: { code?: string; label?: string; occurrence_ref?: string } | null }
export type ReviewDefinition = { ref: string; run_ref: string; label: string; prerequisite_refs?: string[] }
export type GraphSnapshot = { runs: Array<{ ref: string; plan_availability?: string }>; tasks: PlannedTask[]; review_definitions?: ReviewDefinition[]; occurrences: Occurrence[]; records: Observation[]; edges?: GraphEdge[]; chain?: ChainExecution[]; activities?: Activity[] }
export type Followup = { run_ref: string; source_run_ref: string; review_occurrence_ref: string; resolution: string }

export function taskNumber(task: PlannedTask, tasks: PlannedTask[]) {
  const index = tasks.filter(item => item.run_ref === task.run_ref).findIndex(item => item.ref === task.ref)
  return index < 0 ? 'Task' : `Task ${index + 1}`
}
export function taskTitle(task: PlannedTask) {
  const candidate = task.label.trim()
  const title = !candidate || /^task(?:\s|$)/i.test(candidate) || /^[A-Z]+[-_]?\d+$/i.test(candidate) ? 'Recorded task' : candidate
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
export function qualificationText(value: string | null | undefined) {
  return ({ recorded_running: 'Recorded running', outstanding_input: 'Outstanding input', waiting_for_input: 'Waiting for input', incomplete_history: 'Incomplete history', conflicting_terminal_evidence: 'Conflicting completion evidence', incomplete_terminal: 'Incomplete completion evidence' } as Record<string, string>)[value ?? ''] ?? 'Unknown'
}
export function outcomeText(item: Occurrence, records: Observation[]) {
  if (item.execution_summary) return item.execution_summary.state === 'success' ? 'returned — acceptance not established' : item.execution_summary.state === 'failure' ? 'failed' : `${item.execution_summary.state} — ${qualificationText(item.execution_summary.qualification)}`
  if (item.outcome) return item.outcome
  const own = records.filter(record => record.occurrence_ref === item.ref && record.run_ref === item.run_ref)
  if (own.some(record => record.kind === 'returned')) return 'returned — acceptance not established'
  return item.completeness === 'incomplete' ? 'incomplete — outcome unknown' : 'recorded — outcome unknown'
}

/** Projects declared plan slots and only exact recorded calls; relation references never infer identity. */
export function graphFor(root: GraphSnapshot, lineage: GraphSnapshot[], _relations: Followup[]) {
  const snapshots = [root, ...lineage]
  const occurrences = snapshots.flatMap(snapshot => snapshot.occurrences)
  const activities = snapshots.flatMap(snapshot => snapshot.activities ?? [])
  const chain = snapshots.flatMap(snapshot => snapshot.chain ?? [])
  const tasks = snapshots.flatMap(snapshot => snapshot.tasks)
  const definitions = snapshots.flatMap(snapshot => snapshot.review_definitions ?? [])
  const key = (runRef: string, ref: string) => `${runRef}\u0000${ref}`
  const taskFor = (activity: Activity) => activity.task_ref ? tasks.find(task => task.ref === activity.task_ref && task.run_ref === activity.run_ref) : undefined
  const designation = (task: PlannedTask) => taskNumber(task, tasks)
  const occurrenceFor = (activity: Activity) => occurrences.find(item => item.run_ref === activity.run_ref && item.ref === activity.occurrence_ref)
  const presentation = (summary: ExecutionSummary | undefined, outcome: string, rejected = false) => {
    const state = summary?.state ?? (['returned', 'approved', 'rejected'].includes(outcome) ? 'success' : outcome === 'failed' ? 'failure' : 'unknown')
    return { lifecycle: state === 'failure' ? 'failed' : state === 'unknown' ? 'neutral' : state,
      status: state === 'success' ? rejected ? 'returned — changes requested' : 'returned — acceptance not established' : state === 'failure' ? 'failed' : `${state}${summary?.qualification ? ` — ${qualificationText(summary.qualification)}` : ''}` }
  }
  const reviewPresentation = (execution: ChainExecution) => {
    const observed = occurrences.filter(item => item.run_ref === execution.run_ref && (execution.occurrence_refs.includes(item.ref) || activities.some(activity => activity.run_ref === execution.run_ref && activity.role === 'reviewer' && activity.invocation_id === execution.execution_id && activity.occurrence_ref === item.ref)))
    const summaries = observed.map(item => item.execution_summary)
    const summary = summaries.length > 1 ? summaries.every(item => item && item.state === summaries[0]?.state) ? summaries[0] : { state: 'unknown' as const, qualification: 'conflicting_terminal_evidence' } : summaries[0]
    return presentation(summary, execution.outcome, execution.outcome === 'rejected')
  }
  const runStopped = (runRef: string) => occurrences.some(item => item.run_ref === runRef && item.phase === 'terminal' && ['passed', 'failed', 'interrupted', 'abandoned'].includes(item.outcome ?? ''))
  // Public correction-chain entries are opaque activity refs, not private invocation IDs.
  const exactRoot = (activity: Activity, task: PlannedTask) => activity.run_ref === task.run_ref && activity.task_ref === task.ref && activity.role === 'worker' && activity.invocation_kind === 'task_worker' && activity.correction_chain.length === 1 && activity.correction_chain[0] === activity.ref
  const slotId = (runRef: string, ref: string) => `planned-task:${runRef}:${ref}`
  const slotFor = (task: PlannedTask) => slotId(task.run_ref, task.ref)
  const taskMatches = new Map<PlannedTask, Activity[]>()
  for (const task of tasks) taskMatches.set(task, activities.filter(activity => exactRoot(activity, task)))
  const boundActivity = new Map<string, string>()
  const plannedNodes = tasks.map(task => {
    const matches = taskMatches.get(task) ?? []
    const possibleRoots = activities.filter(activity => activity.run_ref === task.run_ref && activity.task_ref === task.ref && activity.role === 'worker' && activity.invocation_kind === 'task_worker')
    const matched = matches.length === 1 ? matches[0] : undefined
    if (matched) boundActivity.set(matched.ref, slotFor(task))
    const unresolved = matches.length > 1 || (!matched && possibleRoots.length > 0)
    const occurrence = matched?.occurrence_ref ? occurrences.find(item => item.run_ref === matched.run_ref && item.ref === matched.occurrence_ref) : undefined
    const qualified = occurrence?.execution_summary
    const state = matched ? qualified ? outcomeText(occurrence!, root.records) : matched.outcome === 'returned' ? 'returned — acceptance not established' : matched.outcome : unresolved ? 'unknown — initial worker reconciliation ambiguous' : task.annotation?.label ?? task.progress?.state ?? 'planned — not started'
    const qualification = unresolved ? 'Initial worker reconciliation ambiguous or incomplete; distinct recorded calls remain separate.' : qualified?.qualification ? qualificationText(qualified.qualification) : null
    const lifecycle = matched ? presentation(qualified, matched.outcome).lifecycle : unresolved ? 'neutral' : task.annotation?.code === 'waiting_for_input' || task.progress?.state === 'blocked' ? 'waiting' : task.progress?.state === 'running' ? 'running' : task.progress?.state === 'unknown' ? 'neutral' : 'pending'
    return { id: slotFor(task), position: { x: 0, y: 0 }, data: { label: `${designation(task)} — Worker — ${taskTitle(task)}`, status: state, identity: { ref: task.ref, runRef: task.run_ref, taskId: task.task_id ?? null, planned: true, invocationId: matched?.invocation_id ?? null }, relationQualification: qualification }, className: `execution-node planned-call ${lifecycle}` } satisfies Node
  })
  const reviewFor = (definition: ReviewDefinition) => `planned-review:${definition.run_ref}:${definition.ref}`
  const boundReview = new Map<string, string>()
  const reviewNodes = definitions.map(definition => {
    const candidates = chain.filter(execution => execution.run_ref === definition.run_ref && execution.role === 'reviewer' && execution.review_ordinal === 1)
    const executionIds = new Set(candidates.map(item => item.execution_id))
    const matched = executionIds.size === 1 ? candidates[0] : undefined
    if (matched) boundReview.set(matched.ref, reviewFor(definition))
    const observed = matched ? reviewPresentation(matched) : undefined
    const state = observed?.status ?? (candidates.length > 1 ? 'unknown — initial review reconciliation ambiguous' : runStopped(definition.run_ref) ? 'Not started; run stopped' : 'planned — not started')
    return { id: reviewFor(definition), position: { x: 0, y: 0 }, data: { label: 'Final review — Independent reviewer', status: state, identity: { ref: definition.ref, runRef: definition.run_ref, planned: true, executionId: matched?.execution_id ?? null }, relationQualification: candidates.length > 1 ? 'Initial review reconciliation ambiguous; distinct recorded reviews remain separate.' : null }, className: `execution-node planned-review ${observed?.lifecycle ?? (candidates.length > 1 ? 'neutral' : 'pending')}` } satisfies Node
  })

  // A review dispatch may be unobserved. Its retained execution ID is still the
  // exact identity for the reviewer activity, so bind it before occurrence lookup.
  for (const execution of chain.filter(item => item.role === 'reviewer')) {
    const matches = activities.filter(activity => activity.run_ref === execution.run_ref && activity.role === 'reviewer' && activity.invocation_id === execution.execution_id)
    if (matches.length === 1 && chain.filter(item => item.run_ref === execution.run_ref && item.execution_id === execution.execution_id).length === 1) boundActivity.set(matches[0].ref, boundReview.get(execution.ref) ?? execution.ref)
  }
  const memberships = new Map<string, string[]>()
  for (const execution of chain.filter(item => item.role !== 'fixer')) for (const occurrence of execution.occurrence_refs) {
    const membershipKey = key(execution.run_ref, occurrence)
    memberships.set(membershipKey, [...(memberships.get(membershipKey) ?? []), execution.ref])
  }
  const occurrenceNode = new Map<string, string>()
  for (const [membershipKey, refs] of memberships) {
    const execution = refs.length === 1 ? chain.find(item => item.ref === refs[0]) : undefined
    if (execution?.occurrence_refs.length === 1) occurrenceNode.set(membershipKey, boundReview.get(execution.ref) ?? execution.ref)
  }
  for (const activity of activities) if (boundActivity.has(activity.ref) && activity.occurrence_ref) occurrenceNode.set(key(activity.run_ref, activity.occurrence_ref), boundActivity.get(activity.ref)!)
  const nodeForOccurrence = (runRef: string, occurrenceRef: string) => occurrenceNode.get(key(runRef, occurrenceRef)) ?? boundActivity.get(activities.find(activity => activity.run_ref === runRef && activity.occurrence_ref === occurrenceRef)?.ref ?? '') ?? activities.find(activity => activity.run_ref === runRef && activity.occurrence_ref === occurrenceRef)?.ref ?? occurrenceRef
  const fixNumber = (activity: Activity) => activity.role === 'fixing_worker' ? activities.filter(candidate => candidate.run_ref === activity.run_ref && candidate.task_ref === activity.task_ref && candidate.role === 'fixing_worker').indexOf(activity) + 1 : activity.correction_chain.filter(ref => activities.some(candidate => candidate.ref === ref && candidate.run_ref === activity.run_ref && candidate.invocation_kind === 'corrective_worker')).length
  const activityNodes = activities.filter(activity => !boundActivity.has(activity.ref) && (!activity.occurrence_ref || !occurrenceNode.has(key(activity.run_ref, activity.occurrence_ref)))).map(activity => {
    const task = taskFor(activity)
    const repeat = activity.role === 'fixing_worker' ? ` — Fix ${fixNumber(activity)}` : activity.invocation_kind === 'corrective_worker' ? ` — Correction ${fixNumber(activity) || 'unknown'}` : ''
    const title = `${task ? `${designation(task)} — ` : ''}${roleName(activity.role)}${repeat}${task ? ` — ${taskTitle(task)}` : ''}`
    const observed = presentation(occurrenceFor(activity)?.execution_summary, activity.outcome)
    return { id: activity.ref, position: { x: 0, y: 0 }, data: { label: title, status: observed.status, identity: { ref: activity.ref, runRef: activity.run_ref, invocationId: activity.invocation_id, taskId: task?.task_id ?? null }, relationQualification: activity.input_qualification === 'recorded' ? null : 'Input relations unknown/not recorded.' }, className: `execution-node actual-call ${observed.lifecycle}` } satisfies Node
  })
  const chainNodes = chain.filter(execution => !boundReview.has(execution.ref) && execution.role !== 'fixer').map(execution => {
    const title = execution.role === 'reviewer' ? `Review ${execution.review_ordinal ?? 'unknown'} — Independent reviewer` : execution.role === 'fixer' ? `Fixing worker${execution.fixing_round == null ? '' : ` round ${execution.fixing_round}`}` : 'Recorded execution'
    const observed = reviewPresentation(execution)
    return { id: execution.ref, position: { x: 0, y: 0 }, data: { label: title, status: observed.status, identity: { ref: execution.ref, runRef: execution.run_ref, executionId: execution.execution_id, occurrenceRefs: execution.occurrence_refs } }, className: `execution-node chain-node actual-call ${observed.lifecycle}` } satisfies Node
  })
  const stopNodes = occurrences.filter(occurrence => occurrence.stopping && !occurrenceNode.has(key(occurrence.run_ref, occurrence.ref)) && !activities.some(activity => activity.run_ref === occurrence.run_ref && activity.occurrence_ref === occurrence.ref)).map(occurrence => ({ id: occurrence.ref, position: { x: 0, y: 0 }, data: { label: 'Execution stopped', status: occurrence.outcome ?? 'cause unknown', identity: { ref: occurrence.ref, runRef: occurrence.run_ref, occurrenceId: occurrence.occurrence_id ?? null }, relationQualification: occurrence.support_ref ? null : 'Stopping cause unknown.' }, className: 'execution-node stop-node failed' } satisfies Node))
  const nodes: Node[] = [...plannedNodes, ...reviewNodes, ...activityNodes, ...chainNodes, ...stopNodes]
  const nodeExists = (id: string) => nodes.some(node => node.id === id)
  const resolve = (ref: string) => boundActivity.get(ref) ?? boundReview.get(ref) ?? ref
  const edges: Edge[] = []
  const edgeByPair = new Map<string, Edge>()
  const rejected = new Map<string, string[]>()
  const reject = (node: string, reason: string) => rejected.set(node, [...(rejected.get(node) ?? []), reason])
  const reaches = (from: string, target: string, seen = new Set<string>()): boolean => from === target || (!seen.has(from) && (seen.add(from), edges.some(edge => edge.source === from && reaches(edge.target, target, seen))))
  const add = (id: string, rawSource: string, rawTarget: string, relation: string, identity: Record<string, unknown>, classification: 'declared' | 'recorded' = 'recorded') => {
    const source = resolve(rawSource), target = resolve(rawTarget)
    if (source === target) { reject(target, 'self relation rejected.'); return }
    if (!nodeExists(source) || !nodeExists(target)) { reject(target, 'Relationship endpoint missing or ambiguous.'); return }
    const pair = `${source}\u0000${target}`
    const existing = edgeByPair.get(pair)
    if (existing) {
      const data = existing.data as { classification: string; classifications: string[]; relations: string[]; identities: Record<string, unknown>[] }
      if (!data.relations.includes(relation)) { data.relations.push(relation); data.identities.push(identity) }
      if (!data.classifications.includes(classification)) data.classifications.push(classification)
      data.classification = data.classifications.length > 1 ? 'mixed' : classification
      existing.className = `${data.classification}-edge`
      return
    }
    if (reaches(target, source)) { reject(target, 'Cyclic relationship rejected.'); return }
    const edge: Edge = { id, source, target, type: 'smoothstep', className: `${classification}-edge`, data: { classification, classifications: [classification], relation, relations: [relation], resolution: 'recorded', identity, identities: [identity] } }
    edgeByPair.set(pair, edge); edges.push(edge)
  }
  for (const task of tasks) for (const prerequisite of task.prerequisite_refs) add(`prerequisite_${prerequisite}_${task.ref}`, slotId(task.run_ref, prerequisite), slotFor(task), 'declared-prerequisite', { prerequisiteRef: prerequisite, taskRef: task.ref }, 'declared')
  for (const definition of definitions) for (const prerequisite of definition.prerequisite_refs ?? []) add(`review_prerequisite_${prerequisite}_${definition.ref}`, slotId(definition.run_ref, prerequisite), reviewFor(definition), 'declared-review-completion', { prerequisiteRef: prerequisite, reviewRef: definition.ref }, 'declared')
  for (const activity of activities) {
    const target = resolve(activity.ref)
    if (!nodeExists(target)) continue
    if (activity.trigger_ref) add(`trigger_${activity.trigger_ref}_${activity.ref}`, activity.trigger_ref, activity.ref, 'recorded-correction-trigger', { triggerRef: activity.trigger_ref, correctionRef: activity.ref })
    if (activity.input_qualification === 'recorded') for (const input of activity.input_refs) add(`input_${input}_${activity.ref}`, input, activity.ref, 'recorded-input', { producerRef: input, consumerRef: activity.ref })
    for (const predecessor of activity.correction_chain.filter(ref => ref !== activity.ref)) add(`correction_${predecessor}_${activity.ref}`, predecessor, activity.ref, 'recorded-correction', { predecessorRef: predecessor, correctionRef: activity.ref })
  }
  for (const execution of chain.filter(item => item.role !== 'fixer')) {
    for (const input of execution.input_refs ?? []) add(`review_input_${input}_${execution.ref}`, input, execution.ref, 'recorded-review-input', { producerRef: input, reviewRef: execution.ref })
    if (execution.trigger_ref) add(`trigger_${execution.trigger_ref}_${execution.ref}`, execution.trigger_ref, execution.ref, 'recorded-correction-trigger', { triggerRef: execution.trigger_ref, executionRef: execution.ref })
    if (execution.predecessor_ref) add(`predecessor_${execution.predecessor_ref}_${execution.ref}`, execution.predecessor_ref, execution.ref, 'recorded-correction-predecessor', { predecessorRef: execution.predecessor_ref, executionRef: execution.ref })
  }
  for (const stop of occurrences.filter(occurrence => occurrence.stopping && occurrence.support_ref)) add(`stop_${stop.ref}`, nodeForOccurrence(stop.run_ref, stop.support_ref!), nodeForOccurrence(stop.run_ref, stop.ref), 'recorded-stop-support', { supportRef: stop.support_ref, stopRef: stop.ref, runRef: stop.run_ref })
  for (const node of nodes) { const qualifications = rejected.get(node.id); if (qualifications?.length) node.data = { ...node.data, relationQualification: qualifications.join(' ') } }
  return { nodes, edges, topology: JSON.stringify({ nodes: nodes.map(node => node.id).sort(), edges: edges.map(edge => [edge.source, edge.target, edge.data?.relation]).sort() }) }
}
export function recordText(record: Observation) {
  const event = ({ started: 'Started', returned: 'Returned', passed: 'Passed', failed: 'Failed', question_requested: 'Waiting for input', answer_returned: 'Answer returned', answer_sent: 'Answer sent', delivery_failed: 'Answer delivery failed' } as Record<string, string>)[record.kind] ?? 'Recorded event'
  return [event, record.ordinal != null ? `check ${record.ordinal}` : '', record.exit_code != null ? `exit ${record.exit_code}` : '', record.approved != null ? record.approved ? 'approved' : 'changes requested' : '', record.finding_count != null ? `${record.finding_count} findings` : '', record.no_change != null ? record.no_change ? 'no changes' : 'changes recorded' : '', record.error_category ? `safe error: ${record.error_category}` : '', record.recording_gap ? 'recording gap' : ''].filter(Boolean).join('; ')
}
