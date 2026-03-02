/**
 * Convert between domain Polygon/Point, editor EditorVertex, and API polygon format.
 *
 * Context: polygonToEditorVertices / editorVerticesToPolygon use @geometry/domain Polygon and Point.
 * apiPolygonToEditorVertices / editorVerticesToApiPolygon use ApiPolygon ({ points: { x, y }[] }) for API payloads.
 * artGalleryToEditorState converts ArtGallery (boundary + obstacles) to flat vertices and edges for the editor.
 *
 * Example:
 *   const verts = polygonToEditorVertices(boundary);  const poly = editorVerticesToPolygon(verts);
 *   const api = editorVerticesToApiPolygon(verts);  // for POST/PATCH body
 *   const { vertices, edges } = artGalleryToEditorState(gallery);
 */

import { ArtGallery, ConvexComponent, Ear, Point, Polygon, Visibility } from "@geometry/domain";
import type { EditorVertex, ApiPolygon } from "./types";

export const polygonToEditorVertices = (polygon: Polygon): EditorVertex[] => {
    return polygon.points.map((p, i) => ({
        id: `v-${i}-${p.x.toFixed(0)}-${p.y.toFixed(0)}`,
        x: p.x,
        y: p.y,
    }));
};

export const editorVerticesToPolygon = (vertices: EditorVertex[]): Polygon => {
    return new Polygon(vertices.map((v) => new Point(v.x, v.y)));
};

export const apiPolygonToEditorVertices = (api: ApiPolygon): EditorVertex[] => {
    const points = api?.points ?? [];
    return points.map((p, i) => ({
        id: `v-${i}-${p.x}-${p.y}`,
        x: p.x,
        y: p.y,
    }));
};

export const editorVerticesToApiPolygon = (vertices: EditorVertex[]): ApiPolygon => {
    return {
        points: vertices.map((v) => ({ x: v.x, y: v.y })),
    };
};

/**
 * Build flat vertices and edges from an ArtGallery (boundary and obstacles only) for the editor/Viewer.
 *
 * Example:
 *   const { vertices, edges } = artGalleryToEditorState(gallery);
 */
export const artGalleryToEditorState = (gallery: ArtGallery): {
    vertices: EditorVertex[];
    edges: [number, number][];
} => {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    let offset = 0;

    const addPolygon = (polygon: Polygon) => {
        const verts = polygonToEditorVertices(polygon);
        const n = verts.length;
        for (let i = 0; i < n; i++) {
            vertices.push(verts[i]);
        }
        for (let i = 0; i < n; i++) {
            edges.push([offset + i, offset + (i + 1) % n] as [number, number]);
        }
        offset += n;
    };

    addPolygon(gallery.boundary);
    for (const obstacle of gallery.obstacles) {
        addPolygon(obstacle);
    }

    return { vertices, edges };
};

/** Canonical key for an undirected edge (same for (a,b) and (b,a)) for O(1) lookup. */
export function edgeKey(
    a: { x: number; y: number },
    b: { x: number; y: number }
): string {
    const [p1, p2] =
        a.x < b.x || (a.x === b.x && a.y < b.y) ? [a, b] : [b, a];
    return `${p1.x},${p1.y}-${p2.x},${p2.y}`;
}

/**
 * Set of edge keys for all edges of boundary and obstacles (for muted styling in viewer modes).
 * Keys are direction-invariant (edgeKey), so one Set supports O(1) membership and avoids
 * quadratic checks when deciding which displayed edges are boundary/obstacle.
 */
export function boundaryObstacleEdgeKeys(boundary: Polygon, obstacles: Polygon[]): Set<string> {
    const keys = new Set<string>();
    const addPolygon = (poly: Polygon) => {
        const pts = poly.points;
        const n = pts.length;
        for (let i = 0; i < n; i++) {
            const p1 = pts[i];
            const p2 = pts[(i + 1) % n];
            keys.add(edgeKey(p1, p2));
        }
    };
    addPolygon(boundary);
    obstacles.forEach(addPolygon);
    return keys;
}

/** Vertices and edges from a single polygon (e.g. stitched). */
export function polygonToEditorState(poly: Polygon): {
    vertices: EditorVertex[];
    edges: [number, number][];
} {
    const vertices = polygonToEditorVertices(poly);
    const n = vertices.length;
    const edges: [number, number][] = [];
    for (let i = 0; i < n; i++) {
        edges.push([i, (i + 1) % n] as [number, number]);
    }
    return { vertices, edges };
}

/** Flat vertices and edges from all ears (each ear = 3 vertices + 3 edges). */
export function earsToEditorState(ears: Ear[]): {
    vertices: EditorVertex[];
    edges: [number, number][];
} {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    let offset = 0;
    ears.forEach((ear: Ear, earIdx: number) => {
        const pts = ear.points;
        for (let i = 0; i < pts.length; i++) {
            vertices.push({
                id: `ear-${earIdx}-${i}-${pts[i].x}-${pts[i].y}`,
                x: pts[i].x,
                y: pts[i].y,
            });
        }
        const n = pts.length;
        for (let i = 0; i < n; i++) {
            edges.push([offset + i, offset + (i + 1) % n] as [number, number]);
        }
        offset += n;
    });
    return { vertices, edges };
}

/** Vertices and edges for visibility: one vertex per guard and per visible point; edges from guard to each visible point (muted in viewer). */
export function visibilityToEditorState(visibility: Visibility[]): {
    vertices: EditorVertex[];
    edges: [number, number][];
} {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    let offset = 0;
    visibility.forEach((vis: Visibility, pathIdx: number) => {
        const guard = vis.guard;
        const path = vis.points;
        vertices.push({
            id: `visibility-guard-${pathIdx}-${guard.x}-${guard.y}`,
            x: guard.x,
            y: guard.y,
        });
        const guardIdx = offset;
        offset += 1;
        for (let i = 0; i < path.length; i++) {
            const p = path[i];
            vertices.push({
                id: `visibility-${pathIdx}-${i}-${p.x}-${p.y}`,
                x: p.x,
                y: p.y,
            });
            edges.push([guardIdx, offset + i] as [number, number]);
        }
        offset += path.length;
    });
    return { vertices, edges };
}

/** Flat vertices and edges from all convex components. */
export function convexComponentsToEditorState(components: ConvexComponent[]): {
    vertices: EditorVertex[];
    edges: [number, number][];
} {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    let offset = 0;
    components.forEach((comp: ConvexComponent, compIdx: number) => {
        const pts = comp.points;
        for (let i = 0; i < pts.length; i++) {
            vertices.push({
                id: `convex-${compIdx}-${i}-${pts[i].x}-${pts[i].y}`,
                x: pts[i].x,
                y: pts[i].y,
            });
        }
        const n = pts.length;
        for (let i = 0; i < n; i++) {
            edges.push([offset + i, offset + (i + 1) % n] as [number, number]);
        }
        offset += n;
    });
    return { vertices, edges };
}

/**
 * Build flat vertices and edges from a list of stitch segments (bridge edges from the stitching step).
 * Used by Viewer in Stitching mode to display only the stitches.
 *
 * Example:
 *   const { vertices, edges } = stitchesToEditorState(gallery.stitches);
 */
export const stitchesToEditorState = (stitches: [Point, Point][]): {
    vertices: EditorVertex[];
    edges: [number, number][];
} => {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    stitches.forEach(([a, b], i) => {
        const ia = i * 2;
        const ib = i * 2 + 1;
        vertices.push({
            id: `stitch-${i}-a-${a.x}-${a.y}`,
            x: a.x,
            y: a.y,
        });
        vertices.push({
            id: `stitch-${i}-b-${b.x}-${b.y}`,
            x: b.x,
            y: b.y,
        });
        edges.push([ia, ib] as [number, number]);
    });
    return { vertices, edges };
};
