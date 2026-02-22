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
