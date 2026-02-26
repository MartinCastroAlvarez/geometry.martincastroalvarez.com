import { ArtGallery, Polygon, Point } from '@geometry/domain'
import { ApiSolveRequest, ApiPolygon, ApiPoint, ApiSolveResponse, ApiVerifyResponse } from './types'

export const domainToApi = (gallery: ArtGallery): ApiSolveRequest => {
    return {
        perimeter: toApiPolygon(gallery.perimeter),
        holes: gallery.holes.map(toApiPolygon)
    }
}

export const toApiPolygon = (polygon: Polygon): ApiPolygon => {
    return {
        points: polygon.points.map(toApiPoint)
    }
}

export const toApiPoint = (point: Point): ApiPoint => {
    return {
        x: point.x,
        y: point.y
    }
}

export const apiToDomain = {
    fromSolveResponse: (response: ApiSolveResponse): { jobId: string } => {
        return { jobId: response.jobId }
    },
    fromVerifyResponse: (response: ApiVerifyResponse): { isValid: boolean; coverage: number } => {
        return {
            isValid: response.isValid,
            coverage: response.coverage
        }
    },
    apiPointToPoint: (p: ApiPoint): Point => Point.fromDict(p),
    apiPolygonToPolygon: (p: ApiPolygon): Polygon => Polygon.fromDict(p)
}
