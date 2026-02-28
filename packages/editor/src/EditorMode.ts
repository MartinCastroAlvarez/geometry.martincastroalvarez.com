/**
 * Editor interaction mode: add vertex, add and connect, or erase.
 *
 * Context: Used by EditorToolbar mode toggle and Editor to decide click behavior
 * (add vertex, add vertex and connect to last, or remove vertex/edge on click).
 */
export enum EditorMode {
    /** Add a vertex on canvas click; no auto-connect. */
    Add = "add",
    /** Add a vertex and connect it to the last one (polyline/polygon). */
    Connect = "connect",
    /** Pan the canvas (move view); geometry unchanged. */
    Move = "move",
    /** Remove vertex or edge on click. */
    Erase = "erase",
}
