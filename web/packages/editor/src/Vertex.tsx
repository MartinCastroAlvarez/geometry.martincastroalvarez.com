import { useState } from 'react'
import { Circle } from 'react-konva'
import type { Vertex } from './types'

interface VertexProps {
    id: string
    position: Vertex
    isFirst?: boolean
    onDragMove: (id: string, position: Vertex) => void
}

export function Vertex({ id, position, isFirst = false, onDragMove }: VertexProps) {
    const [isHovered, setIsHovered] = useState(false)

    return (
        <Circle
            x={position.x}
            y={position.y}
            radius={isHovered ? 10 : (isFirst ? 9 : 6)}
            fill='#3b82f6'
            stroke={isHovered ? '#fff' : '#1e293b'}
            strokeWidth={2}
            draggable
            onDragMove={(e) => {
                onDragMove(id, { id, x: e.target.x(), y: e.target.y() })
            }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            shadowBlur={isHovered ? 10 : 0}
            shadowColor="#000"
            shadowOpacity={0.3}
        />
    )
}
