/**
 * Guard: guard placement point in the art gallery.
 *
 * Context: Subclass of Point with semantic meaning; fromPoint() converts Point to Guard.
 * Reflects backend guards (e.g. Table[Point]).
 *
 * Example:
 *   const g = new Guard(1, 2);  Guard.fromPoint(somePoint);
 */
import { Point } from './Point';

/**
 * Guard: a point representing a guard placement in the art gallery.
 * Reflects backend guards (Table[Point]). Guard is a Point with semantic meaning.
 */
export class Guard extends Point {
    constructor(x: number, y: number) {
        super(x, y);
    }

    static fromPoint(point: Point): Guard {
        return new Guard(point.x, point.y);
    }
}
