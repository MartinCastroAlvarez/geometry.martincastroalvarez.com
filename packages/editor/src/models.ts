import { Point, Polygon } from "@geometry/domain";

/** API format for a point */
export interface ApiPoint {
    x: number;
    y: number;
}

/** API format for a polygon */
export interface ApiPolygon {
    points: ApiPoint[];
}

/** Internal editor vertex with id for React keys */
export interface EditorVertex {
    id: string;
    x: number;
    y: number;
}

export class EditorModel {
    static fromDomain(polygon: Polygon): EditorVertex[] {
        return polygon.points.map((p, i) => ({
            id: `v-${i}-${p.x.toFixed(0)}-${p.y.toFixed(0)}`,
            x: p.x,
            y: p.y,
        }));
    }

    static toDomain(vertices: EditorVertex[]): Polygon {
        return new Polygon(vertices.map((v) => new Point(v.x, v.y)));
    }

    static fromApi(data: ApiPolygon): EditorVertex[] {
        const points = data?.points ?? [];
        return points.map((p, i) => ({
            id: `v-${i}-${p.x}-${p.y}`,
            x: p.x,
            y: p.y,
        }));
    }

    static toApi(vertices: EditorVertex[]): ApiPolygon {
        return {
            points: vertices.map((v) => ({ x: v.x, y: v.y })),
        };
    }
}
