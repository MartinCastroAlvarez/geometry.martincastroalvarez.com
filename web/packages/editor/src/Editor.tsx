import React, { useRef } from 'react'
import { Stage, Layer } from 'react-konva'
import { Container } from '@geometry/ui'
import type { Vertex } from './types'
import { Vertex as VertexComponent } from './Vertex'
import { Edge } from './Edge'

interface EditorProps {
    outerRing: Vertex[]
    holes: Vertex[][]
    currentHole: Vertex[]
    isClosed: boolean
    isAddingHole: boolean
    onAddVertex: (x: number, y: number) => void
    onMoveVertex: (id: string, x: number, y: number) => void
    width?: number
    height?: number
}

export function Editor({
    outerRing,
    holes,
    currentHole,
    isClosed,
    isAddingHole,
    onAddVertex,
    onMoveVertex,
    width = 800,
    height = 600,
}: EditorProps) {
    const stageRef = useRef<any>(null)

    const handleStageClick = (e: any) => {
        // If outer is closed and not adding hole, do nothing (click must be on button to start hole)
        if (isClosed && !isAddingHole) return

        const stage = e.target.getStage()
        const point = stage.getPointerPosition()

        if (!point) return

        // Note: Store handles distance checks and closing logic
        onAddVertex(point.x, point.y)
    }

    const handleVertexDragMove = (id: string, position: { x: number; y: number }) => {
        onMoveVertex(id, position.x, position.y)
    }

    const renderRing = (vertices: Vertex[], isRingClosed: boolean, isHole: boolean = false) => {
        return (
            <>
                {/* Edges */}
                {vertices.length > 1 && vertices.map((vertex, index) => {
                    if (index === vertices.length - 1 && !isRingClosed) {
                        return null
                    }
                    const nextIndex = (index + 1) % vertices.length
                    return (
                        <Edge
                            key={`edge-${isHole ? 'hole' : 'outer'}-${vertex.id}`}
                            start={vertex}
                            end={vertices[nextIndex]}
                            isClosed={isRingClosed}
                        />
                    )
                })}

                {/* Vertices */}
                {vertices.map((vertex, index) => (
                    <VertexComponent
                        key={vertex.id}
                        id={vertex.id}
                        position={vertex}
                        isFirst={index === 0 && !isRingClosed && (!isHole || isAddingHole)} // Only highlight first if open
                        onDragMove={handleVertexDragMove}
                    />
                ))}
            </>
        )
    }

    return (
        <Container solid>
            <Stage
                ref={stageRef}
                width={width}
                height={height}
                onClick={handleStageClick}
                style={{ cursor: (isClosed && !isAddingHole) ? 'default' : 'crosshair', borderRadius: 'inherit' }}
            >
                <Layer>
                    {/* Render Outer Ring */}
                    {renderRing(outerRing, isClosed, false)}

                    {/* Render Existing Holes (Always Closed) */}
                    {holes.map((hole, i) => (
                        <React.Fragment key={`hole-${i}`}>
                            {renderRing(hole, true, true)}
                        </React.Fragment>
                    ))}

                    {/* Render Current Hole (Open) */}
                    {isAddingHole && renderRing(currentHole, false, true)}
                </Layer>
            </Stage>
        </Container>
    )
}
