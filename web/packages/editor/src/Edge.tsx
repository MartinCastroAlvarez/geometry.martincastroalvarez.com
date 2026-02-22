// import React from 'react'
import { Line } from 'react-konva'
import type { Vertex } from './types'

interface EdgeProps {
    start: Vertex
    end: Vertex
    isClosed?: boolean
}

export function Edge({ start, end, isClosed = false }: EdgeProps) {
    return (
        <Line
            points={[start.x, start.y, end.x, end.y]}
            stroke={isClosed ? '#4ade80' : '#64748b'}
            strokeWidth={2}
            lineCap="round"
            lineJoin="round"
        />
    )
}
