import { Polygon, Point } from '@geometry/domain'
import type { Vertex } from './types'

// Simple adapter to convert between Domain Models and Editor Types
// In a real app, we might need stable IDs. For now, we generate IDs based on index 
// or assume the Editor handles ephemeral IDs if needed.

export const objectToDomain = {
    // Convert Editor Vertex array back to Domain Polygon
    verticesToPolygon: (vertices: Vertex[]): Polygon => {
        return new Polygon(vertices.map(v => new Point(v.x, v.y)))
    },

    // Convert raw coords to Point
    coordsToPoint: (x: number, y: number): Point => {
        return new Point(x, y)
    }
}

export const domainToObject = {
    // Convert Domain Polygon to Editor Vertex array (generating IDs)
    polygonToVertices: (polygon: Polygon): Vertex[] => {
        return polygon.points.map((p, i) => ({
            x: p.x,
            y: p.y,
            id: `vertex-${i}-${p.x}-${p.y}` // Simple determinstic ID based on pos/index
        }))
    },

    pointToVertex: (point: Point, index: number): Vertex => {
        return {
            x: point.x,
            y: point.y,
            id: `vertex-${index}-${point.x}-${point.y}`
        }
    }
}
