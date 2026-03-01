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

import { ArtGallery, Point, Polygon } from "@geometry/domain";
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
 * Build flat vertices and edges from an ArtGallery for the editor. When the gallery has stitched,
 * also returns stitchedEdgeIndices: indices of edges that belong only to the stitched polygon
 * (not on boundary or obstacles), so the Viewer can draw them dimmer.
 *
 * Example:
 *   const { vertices, edges, stitchedEdgeIndices } = artGalleryToEditorState(gallery);
 */
export const artGalleryToEditorState = (gallery: ArtGallery): {
    vertices: EditorVertex[];
    edges: [number, number][];
    stitchedEdgeIndices: number[];
} => {
    const vertices: EditorVertex[] = [];
    const edges: [number, number][] = [];
    const stitchedEdgeIndices: number[] = [];
    let offset = 0;

    const boundaryObstacleKeys = new Set<string>();
    const addPolygon = (polygon: Polygon) => {
        const verts = polygonToEditorVertices(polygon);
        const n = verts.length;
        for (let i = 0; i < n; i++) {
            vertices.push(verts[i]);
            const j = (i + 1) % n;
            const a = verts[i];
            const b = verts[j];
            const k1 = `${a.x},${a.y}`;
            const k2 = `${b.x},${b.y}`;
            boundaryObstacleKeys.add(k1 < k2 ? `${k1}|${k2}` : `${k2}|${k1}`);
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

    const stitched = gallery.stitched;
    if (stitched != null && stitched.points.length >= 2) {
        const stitchedVerts = polygonToEditorVertices(stitched);
        const n = stitchedVerts.length;
        for (let i = 0; i < n; i++) {
            vertices.push(stitchedVerts[i]);
        }
        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            const a = stitchedVerts[i];
            const b = stitchedVerts[j];
            const k1 = `${a.x},${a.y}`;
            const k2 = `${b.x},${b.y}`;
            const key = k1 < k2 ? `${k1}|${k2}` : `${k2}|${k1}`;
            if (!boundaryObstacleKeys.has(key)) {
                edges.push([offset + i, offset + j] as [number, number]);
                stitchedEdgeIndices.push(edges.length - 1);
            }
        }
    }

    return { vertices, edges, stitchedEdgeIndices };
};
