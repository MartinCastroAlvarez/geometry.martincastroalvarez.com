/**
 * Visibility: guard point and the ordered list of points forming its visible region.
 *
 * Context: Pairs a guard with its visibility polygon for art gallery viewer.
 * API returns guards and visibility as dicts sharing keys; we build Visibility[]
 * by matching keys so each Visibility has guard and points.
 *
 * Example:
 *   const vis = new Visibility(guard, points);
 *   vis.guard; vis.points;
 */
import { Point, PointDict } from './Point';

export interface VisibilityDict {
    guard: PointDict;
    points: PointDict[];
}

export class Visibility {
    constructor(
        public readonly guard: Point,
        public readonly points: Point[] = []
    ) {}

    static fromDict(dict: VisibilityDict): Visibility {
        const guard = Point.fromDict(dict.guard);
        const points = (dict.points ?? []).map((p) => Point.fromDict(p));
        return new Visibility(guard, points);
    }

    toDict(): VisibilityDict {
        return {
            guard: this.guard.toDict(),
            points: this.points.map((p) => p.toDict()),
        };
    }
}
