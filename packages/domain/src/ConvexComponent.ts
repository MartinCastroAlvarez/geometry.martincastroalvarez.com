/**
 * ConvexComponent: convex polygon used in triangulation/ear-clipping.
 *
 * Context: Extends Polygon; constructor validates convexity via cross-product sign. Reflects backend
 * ConvexComponent. Ear extends this with exactly 3 points.
 *
 * Example:
 *   const c = new ConvexComponent([p1, p2, p3, p4]);  c.isConvex();  // true
 */
import { Point } from './Point';
import { Polygon } from './Polygon';

/**
 * Convex polygon component. Reflects backend ConvexComponent.
 * A polygon that is convex (validated in constructor).
 */
export class ConvexComponent extends Polygon {
    constructor(points: Point[]) {
        super(points);
        if (points.length >= 3 && !this.isConvex()) {
            throw new Error('ConvexComponent must be convex');
        }
    }

    isConvex(): boolean {
        const n = this.points.length;
        if (n < 3) return true;
        let sign = 0;
        for (let i = 0; i < n; i++) {
            const p0 = this.points[i];
            const p1 = this.points[(i + 1) % n];
            const p2 = this.points[(i + 2) % n];
            const cross = (p1.x - p0.x) * (p2.y - p1.y) - (p1.y - p0.y) * (p2.x - p1.x);
            if (cross !== 0) {
                const s = Math.sign(cross);
                if (sign !== 0 && sign !== s) return false;
                sign = s;
            }
        }
        return true;
    }
}
