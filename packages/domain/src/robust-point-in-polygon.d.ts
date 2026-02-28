/**
 * Type declarations for robust-point-in-polygon.
 * -1 = inside, 0 = on boundary, 1 = outside.
 */
declare module 'robust-point-in-polygon' {
    function robustPointInPolygon(ring: [number, number][], point: [number, number]): -1 | 0 | 1;
    export default robustPointInPolygon;
}
