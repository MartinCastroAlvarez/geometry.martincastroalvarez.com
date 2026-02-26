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
