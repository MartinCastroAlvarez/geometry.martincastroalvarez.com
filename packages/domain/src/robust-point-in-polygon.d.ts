declare module 'robust-point-in-polygon' {
    function robustPointInPolygon(ring: [number, number][], point: [number, number]): -1 | 0 | 1;
    export default robustPointInPolygon;
}
