export interface Vertex {
    id: string
    x: number
    y: number
}

export type EditorMode = 'draw' | 'edit' | 'view'

export interface EditorState {
    mode: EditorMode
    snapToGrid: boolean
    gridSize: number
}
