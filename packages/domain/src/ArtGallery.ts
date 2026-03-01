/**
 * ArtGallery and ArtGalleryDict: gallery geometry aligned with API (boundary, obstacles, ears,
 * convex_components, guards, visibility, stitched).
 *
 * Context: Immutable boundary Polygon, obstacles[], guards[]; optional ears, convex_components,
 * visibility, stitched from API. fromDict/toDict for API. Mutations (addObstacle, removeLastObstacle,
 * setBoundary, addGuard) return new instances.
 *
 * Example:
 *   const g = ArtGallery.fromDict({ boundary: {...}, obstacles: [], guards: [] });
 *   g.addObstacle(obstacle).addGuard(guard);  g.toDict();
 *   const withStitched = ArtGallery.fromDict({ ...d, stitched: { points: [...] } });
 */
import { ConvexComponent } from './ConvexComponent';
import { Ear } from './Ear';
import { Point, PointDict } from './Point';
import { Polygon, PolygonDict } from './Polygon';

export interface ArtGalleryDict {
    boundary: PolygonDict;
    obstacles: PolygonDict[];
    guards: PointDict[];
    /** Optional stitched polygon from the stitching step (API). */
    stitched?: PolygonDict;
    /** Optional ears from ear-clipping (API; table or array; values may be PolygonDict or list of coords). */
    ears?: PolygonDict[] | Record<string, PolygonDict | number[][] | unknown>;
    /** Optional convex components from decomposition (API; table or array; values may be PolygonDict or list of coords). */
    convex_components?: PolygonDict[] | Record<string, PolygonDict | number[][] | unknown>;
    /** Optional visibility paths (API; array of paths, each path is array of points). */
    visibility?: PointDict[][];
}

export class ArtGallery {
    constructor(
        public readonly boundary: Polygon,
        public readonly obstacles: Polygon[] = [],
        public readonly guards: Point[] = [],
        /** Optional stitched polygon from the API (edges not on boundary/obstacles). */
        public readonly stitched?: Polygon,
        /** Optional ears from ear-clipping (triangular components). */
        public readonly ears: Ear[] = [],
        /** Optional convex components from decomposition. */
        public readonly convex_components: ConvexComponent[] = [],
        /** Optional visibility paths (each path is a sequence of points). */
        public readonly visibility: Point[][] = []
    ) { }

    static fromDict(dict: ArtGalleryDict): ArtGallery {
        const stitched =
            dict.stitched != null && dict.stitched.points?.length
                ? Polygon.fromDict(dict.stitched)
                : undefined;
        const rawEarList =
            dict.ears == null ? [] : Array.isArray(dict.ears) ? dict.ears : Object.values(dict.ears);
        const toPolyDict = (v: unknown): PolygonDict => {
            if (v != null && typeof v === 'object' && 'points' in v && Array.isArray((v as PolygonDict).points))
                return v as PolygonDict;
            if (Array.isArray(v) && v.length >= 2)
                return { points: v.map((p: unknown) => (Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict)) };
            return { points: [] };
        };
        const ears: Ear[] = rawEarList
            .map(toPolyDict)
            .filter((d) => d.points?.length === 3)
            .map((d) => Ear.fromDict(d));
        const rawConvexList =
            dict.convex_components == null
                ? []
                : Array.isArray(dict.convex_components)
                  ? dict.convex_components
                  : Object.values(dict.convex_components);
        const convex_components: ConvexComponent[] = rawConvexList
            .map(toPolyDict)
            .filter((d) => d.points && d.points.length >= 3)
            .map((d) => ConvexComponent.fromDict(d));
        const visibility: Point[][] = (dict.visibility ?? []).map((path) =>
            path.map(Point.fromDict)
        );
        return new ArtGallery(
            Polygon.fromDict(dict.boundary),
            dict.obstacles.map(Polygon.fromDict),
            dict.guards.map(Point.fromDict),
            stitched,
            ears,
            convex_components,
            visibility
        );
    }

    toDict(): ArtGalleryDict {
        const out: ArtGalleryDict = {
            boundary: this.boundary.toDict(),
            obstacles: this.obstacles.map((o) => o.toDict()),
            guards: this.guards.map((g) => g.toDict())
        };
        if (this.stitched != null && this.stitched.points.length > 0) {
            out.stitched = this.stitched.toDict();
        }
        if (this.ears.length > 0) {
            out.ears = this.ears.map((e) => e.toDict());
        }
        if (this.convex_components.length > 0) {
            out.convex_components = this.convex_components.map((c) => c.toDict());
        }
        if (this.visibility.length > 0) {
            out.visibility = this.visibility.map((path) => path.map((p) => p.toDict()));
        }
        return out;
    }

    addObstacle(obstacle: Polygon): ArtGallery {
        return new ArtGallery(
            this.boundary,
            [...this.obstacles, obstacle],
            this.guards,
            this.stitched,
            this.ears,
            this.convex_components,
            this.visibility
        );
    }

    removeLastObstacle(): ArtGallery {
        if (this.obstacles.length === 0) return this;
        return new ArtGallery(
            this.boundary,
            this.obstacles.slice(0, -1),
            this.guards,
            this.stitched,
            this.ears,
            this.convex_components,
            this.visibility
        );
    }

    setBoundary(boundary: Polygon): ArtGallery {
        return new ArtGallery(
            boundary,
            this.obstacles,
            this.guards,
            this.stitched,
            this.ears,
            this.convex_components,
            this.visibility
        );
    }

    addGuard(guard: Point): ArtGallery {
        return new ArtGallery(
            this.boundary,
            this.obstacles,
            [...this.guards, guard],
            this.stitched,
            this.ears,
            this.convex_components,
            this.visibility
        );
    }
}
