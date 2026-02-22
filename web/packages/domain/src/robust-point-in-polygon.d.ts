declare module 'robust-point-in-polygon' {
    type Point = [number, number];
    type Polygon = Point[];
    /**
     * Returns:
     * -1 if point is strictly inside the polygon
     * 0 if point is on the boundary
     * 1 if point is outside
     */
    function robustPointInPolygon(polygon: Polygon, point: Point): -1 | 0 | 1;
    export = robustPointInPolygon;
}
