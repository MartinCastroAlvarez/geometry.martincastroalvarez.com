/**
 * Editor and API types: vertex with id for keys, and plain point/polygon for API.
 *
 * Context: EditorVertex (id, x, y) is used in editor state; id is for React keys. ApiPoint and ApiPolygon
 * are plain objects ({ x, y }, { points: ApiPoint[] }) for request/response bodies.
 *
 * Example:
 *   const v: EditorVertex = { id: "v-0-10-20", x: 10, y: 20 };
 *   const api: ApiPolygon = { points: [{ x: 0, y: 0 }, { x: 1, y: 0 }] };
 */

/** Internal editor vertex with id for React keys */
export interface EditorVertex {
    id: string;
    x: number;
    y: number;
}

/** API format for a point (editor-specific) */
export interface ApiPoint {
    x: number;
    y: number;
}

/** API format for a polygon (editor-specific) */
export interface ApiPolygon {
    points: ApiPoint[];
}
