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
