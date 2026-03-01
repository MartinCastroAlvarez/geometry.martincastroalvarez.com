/**
 * Ear: triangular ear from ear-clipping algorithm.
 *
 * Context: ConvexComponent with exactly 3 points; constructor throws if points.length !== 3.
 * Reflects backend Ear type used in triangulation. fromDict/toDict for API (same shape as PolygonDict).
 *
 * Example:
 *   const ear = new Ear([p1, p2, p3]);  // must be 3 points
 *   const ear = Ear.fromDict({ points: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0.5, y: 1 }] });
 */
import { Point } from './Point';
import type { PolygonDict } from './Polygon';
import { Polygon } from './Polygon';
import { ConvexComponent } from './ConvexComponent';

/**
 * Ear: triangular ear from ear-clipping. Exactly 3 points, convex.
 * Reflects backend Ear (ConvexComponent with exactly 3 points).
 */
export class Ear extends ConvexComponent {
    constructor(points: Point[]) {
        super(points);
        if (points.length !== 3) {
            throw new Error('Ear must have exactly 3 points');
        }
    }

    static fromDict(dict: PolygonDict): Ear {
        return new Ear(Polygon.fromDict(dict).points);
    }
}
