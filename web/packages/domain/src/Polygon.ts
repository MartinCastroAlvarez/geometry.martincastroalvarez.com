/// <reference path="./robust-point-in-polygon.d.ts" />
import robustPointInPolygon from 'robust-point-in-polygon';
import { Point, PointDict } from './Point';

export interface PolygonDict {
    points: PointDict[];
}

export class Polygon {
    constructor(public readonly points: Point[]) { }

    static fromDict(dict: PolygonDict): Polygon {
        return new Polygon(dict.points.map(Point.fromDict));
    }

    toDict(): PolygonDict {
        return { points: this.points.map(p => p.toDict()) };
    }

    get isClosed(): boolean {
        if (this.points.length < 3) return false;
        const first = this.points[0];
        const last = this.points[this.points.length - 1];
        return first.equals(last);
    }

    /**
     * Checks if a point is strictly inside the polygon.
     * Returns true if inside, false if outside or on boundary.
     */
    contains(point: Point): boolean {
        // robust-point-in-polygon expects [x, y] arrays
        const ring = this.points.map(p => p.toArray());
        // -1: inside, 0: boundary, 1: outside
        const result = robustPointInPolygon(ring, point.toArray());
        return result === -1;
    }

    addPoint(point: Point): Polygon {
        return new Polygon([...this.points, point]);
    }

    removeLastPoint(): Polygon {
        if (this.points.length === 0) return this;
        return new Polygon(this.points.slice(0, -1));
    }
}
