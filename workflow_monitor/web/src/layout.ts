import ELK from 'elkjs/lib/elk.bundled.js'

export type LayoutSize = { width: number; height: number }
export type LayoutMember = { id: string; size: LayoutSize }
export type LayoutGroup = {
  id: string
  kind: 'task' | 'run-review' | 'unassigned'
  header: LayoutSize
  members: LayoutMember[]
}
export type Prerequisite = { source: string; target: string }
export type FootprintLayoutInput = {
  groups: LayoutGroup[]
  prerequisites: Prerequisite[]
  // Secondary relations are intentionally not ELK rank constraints.
  secondaryRelations?: ReadonlyArray<unknown>
}
type ElkInput = {
  id: string
  layoutOptions: Record<string, string>
  children: Array<{ id: string; width: number; height: number }>
  edges: Array<{ id: string; sources: string[]; targets: string[] }>
}
export type LayoutBounds = LayoutSize & { x: number; y: number }
export type PositionedGroup = {
  id: string
  kind: LayoutGroup['kind']
  bounds: LayoutBounds
  header: LayoutBounds
  children: Array<{ id: string; bounds: LayoutBounds }>
}
export type FootprintLayout = { elkInput: ElkInput; groups: PositionedGroup[] }

const elk = new ELK()
const padding = 16
const spacing = 12

function nonNegative(size: LayoutSize): LayoutSize {
  return { width: Math.max(0, size.width), height: Math.max(0, size.height) }
}

function footprint(group: LayoutGroup): LayoutSize {
  const header = nonNegative(group.header)
  const members = group.members.map(member => nonNegative(member.size))
  return {
    width: Math.max(header.width, ...members.map(member => member.width)) + padding * 2,
    height: padding * 2 + header.height + (members.length ? spacing + members.reduce((total, member) => total + member.height, 0) + spacing * Math.max(0, members.length - 1) : 0)
  }
}

/**
 * Lays out owner footprints in absolute graph coordinates. Header and child bounds are
 * absolute too, so a renderer can convert each one to parent-relative coordinates by
 * subtracting its group's bounds.x/y. Only declared prerequisites enter ELK.
 */
export async function layoutFootprints(input: FootprintLayoutInput): Promise<FootprintLayout> {
  const sizes = new Map(input.groups.map(group => [group.id, footprint(group)]))
  const elkInput: ElkInput = {
    id: 'workflow-monitor-footprints',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'DOWN',
      'elk.spacing.nodeNode': '25',
      'elk.layered.spacing.nodeNodeBetweenLayers': '60'
    },
    children: input.groups.map(group => ({ id: group.id, ...sizes.get(group.id)! })),
    edges: input.prerequisites.map((prerequisite, index) => ({
      id: `prerequisite_${index}`,
      sources: [prerequisite.source],
      targets: [prerequisite.target]
    }))
  }
  const layout = await elk.layout(elkInput)
  const positioned = new Map((layout.children ?? []).map(child => [child.id, child]))
  return {
    elkInput,
    groups: input.groups.map(group => {
      const size = sizes.get(group.id)!
      const positionedGroup = positioned.get(group.id)
      const bounds = { x: positionedGroup?.x ?? 0, y: positionedGroup?.y ?? 0, ...size }
      const headerSize = nonNegative(group.header)
      let y = bounds.y + padding
      const header = { x: bounds.x + padding, y, ...headerSize }
      y += header.height
      if (group.members.length) y += spacing
      const children = group.members.map(member => {
        const size = nonNegative(member.size)
        const child = { id: member.id, bounds: { x: bounds.x + padding, y, ...size } }
        y += size.height + spacing
        return child
      })
      return { id: group.id, kind: group.kind, bounds, header, children }
    })
  }
}
