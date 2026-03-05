/**
 * ArtGallery and ArtGalleryDict: gallery geometry aligned with API (boundary, obstacles, ears,
 * convex_components, guards, visibility, stitched, stitches).
 *
 * Context: Immutable boundary Polygon, obstacles[], guards[]; optional ears, convex_components,
 * visibility, stitched, stitches from API. stitches is the list of bridge edges from the stitching step.
 * fromDict/toDict for API. Mutations (addObstacle, removeLastObstacle, setBoundary, addGuard) return new instances.
 *
 * Example:
 *   const g = ArtGallery.fromDict({ boundary: {...}, obstacles: [], guards: [] });
 *   g.addObstacle(obstacle).addGuard(guard);  g.toDict();
 *   const withStitched = ArtGallery.fromDict({ ...d, stitched: { points: [...] }, stitches: [[[0,0],[1,0]]] });
 */
import { ConvexComponent } from './ConvexComponent';
import { Ear } from './Ear';
import { Point, PointDict } from './Point';
import { Polygon, PolygonDict } from './Polygon';
import { Visibility, VisibilityDict } from './Visibility';

export interface ArtGalleryDict {
    boundary: PolygonDict;
    obstacles: PolygonDict[];
    /** Guards as array of points or dict (table) key -> point for API. */
    guards: PointDict[] | Record<string, PointDict | number[]>;
    /** Optional stitched polygon from the stitching step (API). */
    stitched?: PolygonDict;
    /** Optional list of bridge edges from the stitching step; each segment is two points (PointDict or [x,y]). */
    stitches?: Array<[PointDict | number[], PointDict | number[]] | Array<PointDict | number[]>>;
    /** Optional ears from ear-clipping (API; table or array; values may be PolygonDict or list of coords). */
    ears?: PolygonDict[] | Record<string, PolygonDict | number[][] | unknown>;
    /** Optional convex components from decomposition (API; table or array; values may be PolygonDict or list of coords). */
    convex_components?: PolygonDict[] | Record<string, PolygonDict | number[][] | unknown>;
    /** Optional visibility (API dict key->points; or array of paths; or VisibilityDict[]). */
    visibility?: Record<string, PointDict[] | number[][]> | PointDict[][] | VisibilityDict[];
    /** Optional exclusivity (API dict key->points; edges exclusive to each guard). */
    exclusivity?: Record<string, PointDict[] | number[][]> | PointDict[][] | VisibilityDict[];
    /** Optional duration in milliseconds (from job when published). */
    duration?: number;
    /** Optional coverage points (stitched vertices + convex edge midpoints from guard placement). */
    coverage?: PointDict[] | number[][];
}

function parseVisibilityFromDict(dict: ArtGalleryDict): Visibility[] {
    const rawGuards = dict.guards;
    const rawVis = dict.visibility ?? [];
    if (Array.isArray(rawGuards) && Array.isArray(rawVis)) {
        const paths = rawVis as (PointDict[] | number[])[];
        return rawGuards.map((g, i) => {
            const path = paths[i];
            const points = Array.isArray(path) ? path.map((p: unknown) => Point.fromDict(Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict)) : [];
            return new Visibility(Point.fromDict(g), points);
        });
    }
    if (Array.isArray(rawVis) && rawVis.length > 0 && rawVis[0] != null && typeof rawVis[0] === 'object' && 'guard' in (rawVis[0] as object)) {
        return (rawVis as VisibilityDict[]).map((v) => Visibility.fromDict(v));
    }
    if (rawGuards != null && typeof rawGuards === 'object' && !Array.isArray(rawGuards) && rawVis != null && typeof rawVis === 'object' && !Array.isArray(rawVis)) {
        const keys = Object.keys(rawGuards);
        return keys
            .map((k) => {
                const g = (rawGuards as Record<string, unknown>)[k];
                const path = (rawVis as Record<string, unknown>)[k];
                if (!g || !Array.isArray(path)) return null;
                const guard = Point.fromDict(Array.isArray(g) ? { x: Number(g[0]), y: Number(g[1]) } : g as PointDict);
                const points = path.map((p) => Point.fromDict(Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict));
                return new Visibility(guard, points);
            })
            .filter((v): v is Visibility => v != null);
    }
    return [];
}

function parseExclusivityFromDict(dict: ArtGalleryDict): Visibility[] {
    const rawGuards = dict.guards;
    const rawExcl = dict.exclusivity ?? [];
    if (Array.isArray(rawGuards) && Array.isArray(rawExcl)) {
        const paths = rawExcl as (PointDict[] | number[])[];
        return rawGuards.map((g, i) => {
            const path = paths[i];
            const points = Array.isArray(path) ? path.map((p: unknown) => Point.fromDict(Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict)) : [];
            return new Visibility(Point.fromDict(g), points);
        });
    }
    if (rawGuards != null && typeof rawGuards === "object" && !Array.isArray(rawGuards) && rawExcl != null && typeof rawExcl === "object" && !Array.isArray(rawExcl)) {
        const keys = Object.keys(rawGuards);
        return keys
            .map((k) => {
                const g = (rawGuards as Record<string, unknown>)[k];
                const path = (rawExcl as Record<string, unknown>)[k];
                if (!g || !Array.isArray(path)) return null;
                const guard = Point.fromDict(Array.isArray(g) ? { x: Number(g[0]), y: Number(g[1]) } : g as PointDict);
                const points = path.map((p) => Point.fromDict(Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict));
                return new Visibility(guard, points);
            })
            .filter((v): v is Visibility => v != null);
    }
    return [];
}

export class ArtGallery {
    constructor(
        public readonly boundary: Polygon,
        public readonly obstacles: Polygon[] = [],
        public readonly guards: Point[] = [],
        /** Optional stitched polygon from the API (edges not on boundary/obstacles). */
        public readonly stitched?: Polygon,
        /** Optional list of bridge edges from the stitching step; each segment is [Point, Point]. */
        public readonly stitches: [Point, Point][] = [],
        /** Optional ears from ear-clipping (triangular components). */
        public readonly ears: Ear[] = [],
        /** Optional convex components from decomposition. */
        public readonly convex_components: ConvexComponent[] = [],
    /** Optional visibility (one per guard; guard and visible region points). */
    public readonly visibility: Visibility[] = [],
        /** Optional exclusivity (one per guard; points visible only by that guard). */
        public readonly exclusivity: Visibility[] = [],
        /** Optional total run duration in milliseconds (from job when published). */
        public readonly duration?: number,
        /** Optional coverage points (stitched + convex edge midpoints). */
        public readonly coverage: Point[] = []
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
        const visibility: Visibility[] = parseVisibilityFromDict(dict);
        const exclusivity: Visibility[] = parseExclusivityFromDict(dict);
        const rawStitches = dict.stitches ?? [];
        const stitches: [Point, Point][] = rawStitches.map((seg: unknown) => {
            const s = Array.isArray(seg) && seg.length >= 2 ? seg : [];
            const a = s[0];
            const b = s[1];
            const toPoint = (p: unknown): Point =>
                Array.isArray(p) && p.length >= 2
                    ? new Point(Number(p[0]), Number(p[1]))
                    : Point.fromDict(p as PointDict);
            return [toPoint(a), toPoint(b)];
        });
        const guardsList = Array.isArray(dict.guards)
            ? dict.guards.map((g) => Point.fromDict(g))
            : (dict.guards && typeof dict.guards === 'object'
                ? Object.values(dict.guards).map((g: PointDict | number[]) =>
                    Point.fromDict(Array.isArray(g) ? { x: Number(g[0]), y: Number(g[1]) } : g as PointDict)
                  )
                : []);
        const duration =
            dict.duration != null && typeof dict.duration === 'number' && dict.duration >= 0
                ? dict.duration
                : undefined;
        const rawCoverage = dict.coverage;
        const coverage: Point[] =
            Array.isArray(rawCoverage)
                ? rawCoverage.map((p: PointDict | number[]) =>
                    Point.fromDict(Array.isArray(p) ? { x: Number(p[0]), y: Number(p[1]) } : p as PointDict)
                  )
                : [];
        return new ArtGallery(
            Polygon.fromDict(dict.boundary),
            dict.obstacles.map(Polygon.fromDict),
            guardsList,
            stitched,
            stitches,
            ears,
            convex_components,
            visibility,
            exclusivity,
            duration,
            coverage
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
        if (this.stitches.length > 0) {
            out.stitches = this.stitches.map(([a, b]) => [a.toDict(), b.toDict()]);
        }
        if (this.ears.length > 0) {
            out.ears = this.ears.map((e) => e.toDict());
        }
        if (this.convex_components.length > 0) {
            out.convex_components = this.convex_components.map((c) => c.toDict());
        }
        if (this.visibility.length > 0) {
            out.visibility = this.visibility.map((v) => v.toDict());
        }
        if (this.exclusivity.length > 0) {
            out.exclusivity = this.exclusivity.map((v) => v.toDict());
        }
        if (this.duration != null && this.duration >= 0) {
            out.duration = this.duration;
        }
        if (this.coverage.length > 0) {
            out.coverage = this.coverage.map((p) => p.toDict());
        }
        return out;
    }

    addObstacle(obstacle: Polygon): ArtGallery {
        return new ArtGallery(
            this.boundary,
            [...this.obstacles, obstacle],
            this.guards,
            this.stitched,
            this.stitches,
            this.ears,
            this.convex_components,
            this.visibility,
            this.exclusivity,
            this.duration,
            this.coverage
        );
    }

    removeLastObstacle(): ArtGallery {
        if (this.obstacles.length === 0) return this;
        return new ArtGallery(
            this.boundary,
            this.obstacles.slice(0, -1),
            this.guards,
            this.stitched,
            this.stitches,
            this.ears,
            this.convex_components,
            this.visibility,
            this.exclusivity,
            this.duration,
            this.coverage
        );
    }

    setBoundary(boundary: Polygon): ArtGallery {
        return new ArtGallery(
            boundary,
            this.obstacles,
            this.guards,
            this.stitched,
            this.stitches,
            this.ears,
            this.convex_components,
            this.visibility,
            this.exclusivity,
            this.duration,
            this.coverage
        );
    }

    addGuard(guard: Point): ArtGallery {
        return new ArtGallery(
            this.boundary,
            this.obstacles,
            [...this.guards, guard],
            this.stitched,
            this.stitches,
            this.ears,
            this.convex_components,
            this.visibility,
            this.exclusivity,
            this.duration,
            this.coverage
        );
    }
}

