/**
 * Polygon and PolygonDict: closed ring of points and point-in-polygon.
 *
 * Context: Immutable list of Point; fromDict/toDict for API. contains() uses robust-point-in-polygon
 * (-1 = inside). isClosed when first equals last; addPoint/removeLastPoint for editing.
 *
 * Example:
 *   const poly = Polygon.fromDict({ points: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 1 }] });
 *   poly.contains(new Point(0.2, 0.2));  poly.isClosed;
 */
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
        const ring = this.points.map(p => p.toArray());
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
