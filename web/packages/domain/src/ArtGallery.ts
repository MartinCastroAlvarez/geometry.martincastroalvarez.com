import { Point, PointDict } from './Point';
import { Polygon, PolygonDict } from './Polygon';

export interface ArtGalleryDict {
    outer: PolygonDict;
    holes: PolygonDict[];
    guards: PointDict[];
}

export class ArtGallery {
    constructor(
        public readonly perimeter: Polygon,
        public readonly holes: Polygon[] = [],
        public readonly guards: Point[] = []
    ) { }

    static fromDict(dict: ArtGalleryDict): ArtGallery {
        return new ArtGallery(
            Polygon.fromDict(dict.outer),
            dict.holes.map(Polygon.fromDict),
            dict.guards.map(Point.fromDict)
        );
    }

    toDict(): ArtGalleryDict {
        return {
            outer: this.perimeter.toDict(),
            holes: this.holes.map(h => h.toDict()),
            guards: this.guards.map(g => g.toDict())
        };
    }

    addHole(hole: Polygon): ArtGallery {
        return new ArtGallery(this.perimeter, [...this.holes, hole], this.guards);
    }

    removeLastHole(): ArtGallery {
        if (this.holes.length === 0) return this;
        return new ArtGallery(this.perimeter, this.holes.slice(0, -1), this.guards);
    }

    setPerimeter(perimeter: Polygon): ArtGallery {
        return new ArtGallery(perimeter, this.holes, this.guards);
    }

    addGuard(guard: Point): ArtGallery {
        return new ArtGallery(this.perimeter, this.holes, [...this.guards, guard]);
    }
}
