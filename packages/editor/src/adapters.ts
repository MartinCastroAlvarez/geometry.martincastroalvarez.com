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
