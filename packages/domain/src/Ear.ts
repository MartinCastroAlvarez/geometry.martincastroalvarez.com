/**
 * Ear: triangular ear from ear-clipping algorithm.
 *
 * Context: ConvexComponent with exactly 3 points; constructor throws if points.length !== 3.
 * Reflects backend Ear type used in triangulation.
 *
 * Example:
 *   const ear = new Ear([p1, p2, p3]);  // must be 3 points
 */
import { Point } from './Point';
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
}
