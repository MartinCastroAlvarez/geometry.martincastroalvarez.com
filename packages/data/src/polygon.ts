/**
 * Types for polygon validation (boundary and obstacles).
 *
 * Context: useValidatePolygon lives in job.ts. This file only exports
 * ValidatePolygonParams for type safety when calling validation with domain Polygon.
 */

import type { Polygon } from "@geometry/domain";

export interface ValidatePolygonParams {
    boundary: Polygon;
    obstacles: Polygon[];
}
