import { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Background, Controls, ReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Mockup-only fixture adapter. Interaction props below match web/src/main.tsx.
let clearGraphSelection = () => {};
function SampleGraph({ fixture }) {
  const [nodes, setNodes] = useState(() => fixture.nodes.map(node => ({
    id: node.id, position: { x: node.x, y: node.y },
    data: { label: <><strong>{node.title}</strong><small>{node.state}</small></> },
    className: `execution-node ${node.color}`
  })));
  const [selection, setSelection] = useState(null);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });
  const [flow, setFlow] = useState(null);
  useEffect(() => {
    if (!flow) return;
    // Measure the rendered fixture, as main.tsx does before its layout/initial fit.
    // Retain dimensions so selection does not hide nodes/edges for remeasurement.
    const frame = requestAnimationFrame(() => {
      const sizes = new Map([...document.querySelectorAll('#graph .execution-node')].map(element =>
        [element.dataset.id, { width: element.offsetWidth, height: element.offsetHeight }]));
      setNodes(current => current.map(node => ({ ...node, measured: sizes.get(node.id) })));
      void flow.fitView({ padding: .12, maxZoom: 1 });
    });
    return () => cancelAnimationFrame(frame);
  }, [flow]);
  useEffect(() => { clearGraphSelection = () => setSelection(null); return () => { clearGraphSelection = () => {}; }; }, []);
  // Like production, viewport-only moves do not recreate node objects.
  const renderedNodes = useMemo(() => nodes.map(node => ({ ...node,
    selected: selection?.kind === 'node' && selection.id === node.id
  })), [nodes, selection]);
  const edges = useMemo(() => fixture.edges.map((edge, index) => ({
    id: `edge-${index}`, source: edge[0], target: edge[1], type: 'smoothstep',
    selected: selection?.kind === 'edge' && selection.id === `edge-${index}`,
    data: { relation: edge[2] }
  })), [fixture, selection]);
  return <ReactFlow nodes={renderedNodes} edges={edges}
    onInit={setFlow} minZoom={.15}
    viewport={viewport} onMove={(_, next) => setViewport(next)}
    onNodeDragStop={(_, node) => setNodes(current => current.map(item => item.id === node.id ? { ...item, position: node.position } : item))}
    onNodeClick={(_, node) => { setSelection({ kind: 'node', id: node.id }); showDetails(fixture.nodes.find(item => item.id === node.id)); }}
    onEdgeClick={(_, edge) => { setSelection({ kind: 'edge', id: edge.id }); showDetails(null, fixture.edges[Number(edge.id.slice(5))]); }}>
    <Background />
    <Controls />
  </ReactFlow>;
}
const graphRoot = createRoot(document.getElementById('graph'));

/* DEMO DATA AND INTERACTION ONLY. These are not API DTOs or a new status inference layer. */
// label is the retained original run_id, not a human-name field or qualified route ID.
const runs = [
  { id: 'current', label: 'review-convergence-20261024', worktree: 'curvy-skunk', qualifier: 'Run 2', when: 'Today, 10:40', source: 'linked', state: 'Recorded running · sample', summary: 'Full-range acceptance: not established. No final independent review intent is supplied in this sample. The failed initial call and its later running correction remain separate.' },
  { id: 'earlier', label: 'review-convergence-20261023', worktree: 'curvy-skunk', qualifier: 'Run 1', when: 'Yesterday, 16:20', source: 'linked', state: 'Stopped · sample', summary: 'Full-range acceptance: not established. The reviewer returned with changes requested. The corrective call was interrupted; an explicit stopping step remains visible.' },
  { id: 'legacy', label: '7b2e4a4cf7cb4a659d268cb12e93a407', worktree: null, qualifier: '', when: 'Earlier recording', source: 'preserved', state: 'Incomplete recording · sample', summary: 'Plan unavailable in this older sample recording. Do not infer task slots or rebuild task descriptions from current files.' }
];
// Node dimensions and fixture coordinates are illustrative. Production must measure content.
const fixtures = {
  current: {
    nodes: [
      { id:'t1', x:24, y:24, title:'Task 1 · Read project inventory', role:'Worker', state:'Returned · acceptance not established', color:'success', work:'Read the registered project inventory without modifying its stores.' },
      { id:'t3', x:276, y:24, title:'Task 3 · Match run sources', role:'Worker', state:'Failed · transport error', color:'failed', work:'Match each listed run to its retained recording source.' },
      { id:'t4', x:528, y:24, title:'Task 4 · Confirm run labels', role:'Planned worker', state:'Waiting for input · not started', color:'failed', work:'Confirm the original run identifier and worktree folder label.', blocker:'A task-scoped question is outstanding. Waiting is not running.' },
      { id:'t2', x:24, y:158, title:'Task 2 · Label projects', role:'Worker', state:'Returned · acceptance not established', color:'success', work:'Use the registered main directory name as the project label.' },
      { id:'fix', x:276, y:158, title:'Task 3 · Corrective worker 1', role:'Corrective worker', state:'Running · recorded, not live proof', color:'running', work:'Match each listed run to its retained recording source.' },
      { id:'t6', x:528, y:158, title:'Task 6 · Show worktree name', role:'Planned worker', state:'Blocked · Task 4 needs input', color:'failed', work:'Show only the final worktree folder name beside the original run identifier.', blocker:'Task 4 needs input.' },
      { id:'t5', x:24, y:292, title:'Task 5 · Check project labels', role:'Planned worker', state:'Not started', color:'pending', work:'Check that project labels remain readable in the run selector.' },
      { id:'t7', x:276, y:426, title:'Task 7 · Description unavailable', role:'Planned worker', state:'Blocked · prerequisite incomplete', color:'failed', work:null, blocker:'Task 6 has not completed.' }
    ],
    edges: [
      ['t1','t2','Declared prerequisite and recorded input'],
      ['t3','fix','Recorded correction predecessor'],
      ['t4','t6','Declared prerequisite; not proof of execution'],
      ['t2','t5','Declared prerequisite; not proof of execution'],
      ['t5','t7','Declared prerequisite; not proof of execution'],
      ['t6','t7','Declared prerequisite; not proof of execution']
    ]
  },
  earlier: {
    nodes: [
      { id:'a', x:24, y:24, title:'Task 1 · Read project inventory', role:'Worker', state:'Returned · acceptance not established', color:'success', work:'Read the registered project inventory without modifying its stores.' },
      { id:'b', x:528, y:24, title:'Task 2 · Label projects', role:'Worker', state:'Returned · acceptance not established', color:'success', work:'Use the registered main directory name as the project label.' },
      { id:'review', x:276, y:158, title:'Review 1 · Independent reviewer', role:'Reviewer', state:'Returned · changes requested', color:'success', work:null, acceptance:'Approved: false. Findings: 1. Full-range acceptance: not established.', blocker:'The reviewer requested changes.' },
      { id:'repair', x:276, y:292, title:'Task 2 · Corrective worker 1', role:'Corrective worker', state:'Interrupted · outcome unknown', color:'failed', work:'Use the registered main directory name as the project label.' },
      { id:'stop', x:276, y:426, title:'Execution stopped', role:'Stopping step', state:'Failed · correction interrupted', color:'failed', work:null }
    ],
    edges: [
      ['a','review','Recorded review input'],
      ['b','review','Recorded review input'],
      ['review','repair','Recorded correction trigger'],
      ['repair','stop','Recorded stopping support']
    ]
  },
  legacy: { nodes:[], edges:[] }
};
let project = 'sample-tools', run = runs[0], selected = null;
const $ = id => document.getElementById(id);
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value; return element; };
const runLabel = item => `${item.label} · ${item.worktree ?? 'Worktree name unavailable'}`;
function showRuns() {
  const filter = $('filter').value.toLowerCase();
  const available = project === 'sample-tools' ? runs : [];
  $('runs').replaceChildren();
  for (const item of available.filter(item => `${runLabel(item)} ${item.qualifier} ${item.source}`.toLowerCase().includes(filter))) {
    const button = document.createElement('button');
    button.className = item === run ? 'selected' : '';
    button.setAttribute('aria-pressed', String(item === run));
    button.append(text('strong', runLabel(item)), text('small', [item.qualifier, item.when, item.source].filter(Boolean).join(' · ')));
    button.onclick = () => { run = item; showRuns(); render(); };
    $('runs').append(button);
  }
  const outside = run && !`${runLabel(run)} ${run.qualifier} ${run.source}`.toLowerCase().includes(filter);
  $('filter-note').hidden = !!$('runs').children.length && !outside;
  $('filter-note').textContent = !available.length ? 'No recorded runs.' : !$('runs').children.length ? 'No runs match. The selection is unchanged.' : 'The selected run is outside this filter.';
}
function closeDetails() {
  selected = null;
  $('selection-details').hidden = true;
  $('execution-view').classList.remove('has-selection');
  clearGraphSelection();
}
function disclose(summary, body) {
  const details = document.createElement('details'); details.append(text('summary', summary), text('p', body)); return details;
}
function showDetails(node, edge) {
  selected = node?.id ?? null;
  const content = $('selection-content'); content.replaceChildren();
  if (node) {
    content.append(text('h3', node.title), text('p', `${node.role} · ${node.state}`));
    if (node.role.includes('worker') || node.role === 'Worker') content.append(text('p', node.work ?? 'Task description unavailable: this recording did not retain task work text.'));
    if (node.blocker) content.append(text('p', node.blocker));
    content.append(text('p', node.acceptance ?? 'Acceptance: not established. A returned call does not prove task completion or accepted work.'));
    content.append(disclose('Checks and acceptance', node.acceptance ?? 'Checks and focused checkpoint evidence: unavailable in this sample. Do not infer a successful checkpoint from a returned worker.'));
    content.append(disclose('Metrics', 'This call: unavailable. Task total: unavailable. Overall run: unavailable. Session totals are not call spend.'));
    content.append(disclose('Recorded history', 'Synthetic state only. No recorded events are loaded by this mockup.'));
  } else {
    const nodes = fixtures[run.id].nodes;
    content.append(text('h3', 'Relationship'), text('p', `${nodes.find(n => n.id === edge[0]).title} → ${nodes.find(n => n.id === edge[1]).title}`), text('p', edge[2]));
    content.append(text('p', 'One visual edge style. The relation meaning is retained here; declared prerequisites do not prove execution.'));
  }
  $('selection-details').hidden = false; $('execution-view').classList.add('has-selection');

}
function render() {
  closeDetails();
  $('run-heading').textContent = run ? `${runLabel(run)}${run.qualifier ? ` · ${run.qualifier}` : ''}` : project;
  $('run-status').textContent = run?.state ?? 'No recorded runs · sample';
  $('evidence-summary').textContent = run?.summary ?? 'No run selected.';
  $('evidence').open = false;
  const fixture = run ? fixtures[run.id] : { nodes:[], edges:[] };
  $('graph-help').hidden = !fixture.nodes.length;
  graphRoot.render(fixture.nodes.length
    ? <SampleGraph key={run.id} fixture={fixture} />
    : <p className="empty" id="empty">{run ? 'Planned graph unavailable: this older recording has no supported task description. No tasks or calls are invented.' : 'No recorded runs for this sample project.'}</p>);
}
$('close-details').onclick = () => { const node = document.querySelector(`.execution-node[data-id="${selected}"]`); closeDetails(); node?.focus(); };
$('filter').oninput = showRuns;
for (const button of document.querySelectorAll('[data-project]')) button.onclick = () => {
  project = button.dataset.project; run = project === 'sample-tools' ? runs[0] : null; $('filter').value = '';
  document.querySelectorAll('[data-project]').forEach(item => { item.classList.toggle('selected', item === button); item.setAttribute('aria-pressed', String(item === button)); });
  showRuns(); render();
};
showRuns(); render();
