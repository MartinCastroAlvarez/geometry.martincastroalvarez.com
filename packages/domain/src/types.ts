/**
 * SolveRequest and SolveResponse: art-gallery solve API contract.
 *
 * Context: SolveRequest is outer polygon, holes, and guards (all Dict form). SolveResponse is
 * solution points, coverage (0–1), and isValid. Used by geometry/solve API layer.
 *
 * Example:
 *   const req: SolveRequest = { outer: {...}, holes: [], guards: [] };
 *   const res: SolveResponse = { solution: [], coverage: 1, isValid: true };
 */
import { PointDict } from './Point'
import { PolygonDict } from './Polygon'

export interface SolveRequest {
    outer: PolygonDict
    holes: PolygonDict[]
    guards: PointDict[]
}

export interface SolveResponse {
    solution: PointDict[]
    coverage: number // 0-1
    isValid: boolean
}
