/**
 * @geometry/editor public API: canvas editor, edge/vertex components, toolbar, types and adapters.
 *
 * Context: Re-exports Editor (main canvas), Edge, Vertex (Konva shapes), Toolbar, EditorVertex/ApiPolygon types,
 * and polygon/editor/API conversion helpers (polygonToEditorVertices, editorVerticesToPolygon, etc.).
 *
 * Example:
 *   import { Editor, EditorVertex, polygonToEditorVertices } from "@geometry/editor";
 */

export * from './Edge'
export * from './Editor'
export * from './EditorMode'
export * from './Editor.skeleton'
export * from './EditorReview'
export * from './EditorReview.skeleton'
export * from './EditorToolbar'
export * from './Polygon.skeleton'
export * from './types'
export * from './adapters'
