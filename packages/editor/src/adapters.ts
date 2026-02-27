import { Point, Polygon } from "@geometry/domain";
import type { EditorVertex, ApiPolygon } from "./types";

export function polygonToEditorVertices(polygon: Polygon): EditorVertex[] {
    return polygon.points.map((p, i) => ({
        id: `v-${i}-${p.x.toFixed(0)}-${p.y.toFixed(0)}`,
        x: p.x,
        y: p.y,
    }));
}

export function editorVerticesToPolygon(vertices: EditorVertex[]): Polygon {
    return new Polygon(vertices.map((v) => new Point(v.x, v.y)));
}

export function apiPolygonToEditorVertices(api: ApiPolygon): EditorVertex[] {
    const points = api?.points ?? [];
    return points.map((p, i) => ({
        id: `v-${i}-${p.x}-${p.y}`,
        x: p.x,
        y: p.y,
    }));
}

export function editorVerticesToApiPolygon(vertices: EditorVertex[]): ApiPolygon {
    return {
        points: vertices.map((v) => ({ x: v.x, y: v.y })),
    };
}
