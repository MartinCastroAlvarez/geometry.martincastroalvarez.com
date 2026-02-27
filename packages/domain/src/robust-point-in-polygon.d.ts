/**
 * Type declarations for robust-point-in-polygon.
 *
 * Context: -1 = inside, 0 = on boundary, 1 = outside. Used by Polygon.contains().
 */
declare module 'robust-point-in-polygon' {
    function robustPointInPolygon(ring: [number, number][], point: [number, number]): -1 | 0 | 1;
    export default robustPointInPolygon;
}
