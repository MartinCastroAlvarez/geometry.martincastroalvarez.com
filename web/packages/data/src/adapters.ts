import { ArtGallery, Polygon, Point } from '@geometry/domain'
import { ApiSolveRequest, ApiPolygon, ApiPoint } from './types'

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
