/**
 * ArtGallery and ArtGalleryDict: gallery geometry (boundary, obstacles, guards).
 *
 * Context: Immutable boundary Polygon, obstacles[], guards[]; fromDict/toDict for API. Mutations
 * (addObstacle, removeLastObstacle, setBoundary, addGuard) return new instances.
 *
 * Example:
 *   const g = ArtGallery.fromDict({ boundary: {...}, obstacles: [], guards: [] });
 *   g.addObstacle(obstacle).addGuard(guard);  g.toDict();
 */
import { Point, PointDict } from './Point';
import { Polygon, PolygonDict } from './Polygon';

export interface ArtGalleryDict {
    boundary: PolygonDict;
    obstacles: PolygonDict[];
    guards: PointDict[];
}

export class ArtGallery {
    constructor(
        public readonly boundary: Polygon,
        public readonly obstacles: Polygon[] = [],
        public readonly guards: Point[] = []
    ) { }

    static fromDict(dict: ArtGalleryDict): ArtGallery {
        return new ArtGallery(
            Polygon.fromDict(dict.boundary),
            dict.obstacles.map(Polygon.fromDict),
            dict.guards.map(Point.fromDict)
        );
    }

    toDict(): ArtGalleryDict {
        return {
            boundary: this.boundary.toDict(),
            obstacles: this.obstacles.map(o => o.toDict()),
            guards: this.guards.map(g => g.toDict())
        };
    }

    addObstacle(obstacle: Polygon): ArtGallery {
        return new ArtGallery(this.boundary, [...this.obstacles, obstacle], this.guards);
    }

    removeLastObstacle(): ArtGallery {
        if (this.obstacles.length === 0) return this;
        return new ArtGallery(this.boundary, this.obstacles.slice(0, -1), this.guards);
    }

    setBoundary(boundary: Polygon): ArtGallery {
        return new ArtGallery(boundary, this.obstacles, this.guards);
    }

    addGuard(guard: Point): ArtGallery {
        return new ArtGallery(this.boundary, this.obstacles, [...this.guards, guard]);
    }
}
