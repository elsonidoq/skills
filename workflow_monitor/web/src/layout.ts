import ELK from 'elkjs/lib/elk.bundled.js'

export type LayoutSize = { width: number; height: number }
export type LayoutNode = { id: string; size: LayoutSize }
export type LayoutEdge = { source: string; target: string }
type ElkInput = {
  id: string
  layoutOptions: Record<string, string>
  children: Array<{ id: string; width: number; height: number }>
  edges: Array<{ id: string; sources: string[]; targets: string[] }>
}
export type PositionedNode = { id: string; width: number; height: number; x: number; y: number }
export type FlatLayout = { elkInput: ElkInput; nodes: PositionedNode[] }

const elk = new ELK()

function measured(size: LayoutSize): LayoutSize {
  return { width: Math.max(1, size.width), height: Math.max(1, size.height) }
}

/** Lay out the rendered activity calls themselves. Only validated graph edges rank them. */
export async function layoutNodes(nodes: LayoutNode[], edges: LayoutEdge[]): Promise<FlatLayout> {
  const sizes = new Map(nodes.map(node => [node.id, measured(node.size)]))
  const elkInput: ElkInput = {
    id: 'workflow-monitor-activity',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'DOWN',
      'elk.spacing.nodeNode': '25',
      'elk.layered.spacing.nodeNodeBetweenLayers': '60'
    },
    children: nodes.map(node => ({ id: node.id, ...sizes.get(node.id)! })),
    edges: edges.map((edge, index) => ({ id: `relation_${index}`, sources: [edge.source], targets: [edge.target] }))
  }
  const layout = await elk.layout(elkInput)
  const positioned = new Map((layout.children ?? []).map(node => [node.id, node]))
  return {
    elkInput,
    nodes: nodes.map(node => ({ id: node.id, ...sizes.get(node.id)!, x: positioned.get(node.id)?.x ?? 0, y: positioned.get(node.id)?.y ?? 0 }))
  }
}
