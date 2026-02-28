/**
 * Point and PointDict: 2D coordinates and serialization.
 *
 * Context: Immutable (x, y) with fromDict/toDict for API; equals, distanceTo, toArray for geometry.
 * Base for Polygon vertices and Guard positions.
 *
 * Example:
 *   const p = Point.fromDict({ x: 1, y: 2 });  p.toArray();  // [1, 2]
 *   p.equals(q);  p.distanceTo(q);
 */
export interface PointDict {
    x: number;
    y: number;
}

export class Point {
    constructor(public readonly x: number, public readonly y: number) { }

    static fromDict(dict: PointDict): Point {
        return new Point(dict.x, dict.y);
    }

    toDict(): PointDict {
        return { x: this.x, y: this.y };
    }

    equals(other: Point): boolean {
        return Math.abs(this.x - other.x) < Number.EPSILON && Math.abs(this.y - other.y) < Number.EPSILON;
    }

    distanceTo(other: Point): number {
        return Math.sqrt(Math.pow(this.x - other.x, 2) + Math.pow(this.y - other.y, 2));
    }

    toArray(): [number, number] {
        return [this.x, this.y];
    }
}
