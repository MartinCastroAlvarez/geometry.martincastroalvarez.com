/**
 * Geometry calculations for the editor: cycle detection, signed area, point-in-polygon.
 */

import { Point } from "@geometry/domain";
import type { EditorVertex } from "./types";
import { editorVerticesToPolygon } from "./adapters";

/** Find cycles (closed polygons) from vertices and edges. Returns ordered vertex arrays. */
export function findCycles(
    vertices: EditorVertex[],
    edges: [number, number][]
): EditorVertex[][] {
    const n = vertices.length;
    const adj: number[][] = Array.from({ length: n }, () => []);
    for (const [a, b] of edges) {
        if (a >= 0 && a < n && b >= 0 && b < n && a !== b) {
            adj[a].push(b);
            adj[b].push(a);
        }
    }

    const cycles: EditorVertex[][] = [];
    const used = new Set<string>();

    for (let start = 0; start < n; start++) {
        if (adj[start].length !== 2) continue;

        const cycle: number[] = [];
        let v = start;
        let prev = -1;
        let valid = true;

        for (let i = 0; i <= n; i++) {
            if (i > 0 && v === start) break;
            cycle.push(v);
            const nexts = adj[v].filter((u) => u !== prev);
            if (nexts.length !== 1) {
                valid = false;
                break;
            }
            prev = v;
            v = nexts[0];
        }

        if (!valid || v !== start || cycle.length < 3) continue;

        const key = cycle.slice().sort((a, b) => a - b).join(",");
        if (used.has(key)) continue;
        used.add(key);

        cycles.push(cycle.map((i) => vertices[i]));
    }

    return cycles;
}

/** Signed area of a polygon (positive = counterclockwise) */
export function signedArea(vertices: EditorVertex[]): number {
    let area = 0;
    const n = vertices.length;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += vertices[i].x * vertices[j].y - vertices[j].x * vertices[i].y;
    }
    return area / 2;
}

/** Check if cycle A is inside cycle B (point-in-polygon) */
export function isInside(a: EditorVertex[], b: EditorVertex[]): boolean {
    if (a.length === 0 || b.length === 0) return false;
    const p = new Point(a[0].x, a[0].y);
    const poly = editorVerticesToPolygon(b);
    return poly.contains(p);
}
