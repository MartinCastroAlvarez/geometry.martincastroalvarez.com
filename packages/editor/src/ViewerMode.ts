/**
 * Viewer display mode: which geometry to show (polygon only, stitched, ears, etc.).
 *
 * Context: Used by ViewerToolbar and Viewer. Only one mode is active; polygon (DEFAULT)
 * shows boundary and obstacles; STITCHING also shows stitched edges. Other modes are
 * reserved for future use.
 */
export enum ViewerMode {
    /** Boundary and obstacles only (default polygon view). */
    Default = "default",
    /** Ear-clipping triangulation view (reserved). */
    EarClipping = "ear_clipping",
    /** Convex decomposition view (reserved). */
    ConvexComponent = "convex_component",
    /** Boundary, obstacles, and stitched polygon edges. */
    Stitching = "stitching",
    /** Coverage points (stitched + convex edge midpoints) as diamonds. */
    Coverage = "coverage",
    /** Visibility / guards view. */
    Visibility = "visibility",
    /** Exclusivity: edges exclusive to each guard; boundary/obstacles muted. */
    Exclusivity = "exclusivity",
}
