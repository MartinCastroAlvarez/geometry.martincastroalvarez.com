import { useState, useEffect, useCallback } from 'react'
import { Editor, Toolbar, domainToObject } from '@geometry/editor'
import { Toaster, Nav, toast, Container, Title, Text } from '@geometry/ui'
import { useEditor } from './store'
import { Point, Polygon } from '@geometry/domain'
import './index.css'

function App() {
    const { gallery, setPerimeter, setHoles, reset } = useEditor(state => state)
    // Local UI state
    const [mode, setMode] = useState<'draw_perimeter' | 'draw_hole' | 'view'>('draw_perimeter')
    const [currentHolePoints, setCurrentHolePoints] = useState<Point[]>([])

    // Derived state
    const isClosed = gallery.perimeter.isClosed
    const isAddingHole = mode === 'draw_hole'

    // Update mode based on perimeter state if needed
    useEffect(() => {
        if (isClosed && mode === 'draw_perimeter') {
            setMode('view')
        }
        if (!isClosed && mode !== 'draw_perimeter') {
            setMode('draw_perimeter')
        }
    }, [isClosed])

    const handleAddVertex = useCallback((x: number, y: number) => {
        const point = new Point(x, y)

        if (mode === 'draw_perimeter') {
            // Closing logic
            if (gallery.perimeter.points.length >= 3) {
                const first = gallery.perimeter.points[0]
                if (first.distanceTo(point) < 15) {
                    setPerimeter(gallery.perimeter.addPoint(first))
                    return
                }
            }
            setPerimeter(gallery.perimeter.addPoint(point))
        } else if (mode === 'draw_hole') {
            // Check generic containment in outer
            if (!gallery.perimeter.contains(point)) {
                toast.error('Hole must be inside perimeter')
                return
            }

            // Closing hole logic
            if (currentHolePoints.length >= 3) {
                const first = currentHolePoints[0]
                if (first.distanceTo(point) < 15) {
                    const newHole = new Polygon([...currentHolePoints, first]) // Closed hole
                    setHoles([...gallery.holes, newHole])
                    setCurrentHolePoints([])
                    setMode('view') // Return to view after hole
                    toast.success('Hole added')
                    return
                }
            }
            setCurrentHolePoints(prev => [...prev, point])
        }
    }, [gallery.perimeter, gallery.holes, mode, currentHolePoints, setPerimeter, setHoles])

    const handleStartHole = useCallback(() => {
        setMode('draw_hole')
        setCurrentHolePoints([])
        toast.info('Draw hole inside polygon')
    }, [])

    const handleUndo = useCallback(() => {
        if (mode === 'draw_hole') {
            if (currentHolePoints.length > 0) {
                setCurrentHolePoints(prev => prev.slice(0, -1))
            } else {
                setMode('view')
            }
        } else if (mode === 'draw_perimeter') {
            if (gallery.perimeter.points.length > 0) {
                setPerimeter(gallery.perimeter.removeLastPoint())
            }
        }
    }, [mode, currentHolePoints.length, gallery.perimeter.points.length, setPerimeter, gallery.perimeter])

    const handleClear = useCallback(() => {
        reset()
        setMode('draw_perimeter')
        setCurrentHolePoints([])
    }, [reset])

    // Adapter usage
    const outerVertices = domainToObject.polygonToVertices(gallery.perimeter)
    const holeVertices = gallery.holes.map(h => domainToObject.polygonToVertices(h))

    // Current hole visualization (it's local state, map to adapter)
    const currentHolePoly = new Polygon(currentHolePoints)
    const currentHoleVertices = domainToObject.polygonToVertices(currentHolePoly)

    return (
        <div className="min-h-screen bg-slate-50 font-sans">
            <Toaster />
            <Nav />
            <Container padded size={12}>
                <Container size={8} center>
                    <div className="mb-8 text-center">
                        <Title size={2} center>
                            🎨 Geometry Art Gallery Editor
                        </Title>
                        <Text center size={600}>
                            Editor visual interactivo para el Art Gallery Problem
                        </Text>
                    </div>

                    <Toolbar
                        outerRing={outerVertices}
                        holes={holeVertices}
                        currentHole={currentHoleVertices}
                        isClosed={isClosed}
                        isAddingHole={isAddingHole}
                        onUndo={handleUndo}
                        onStartHole={handleStartHole}
                        onClosePolygon={() => { }} // Handled by click logic mostly
                        onClear={handleClear}
                    />

                    <Editor
                        outerRing={outerVertices}
                        holes={holeVertices}
                        currentHole={currentHoleVertices}
                        isClosed={isClosed}
                        isAddingHole={isAddingHole}
                        onAddVertex={handleAddVertex}
                        onMoveVertex={() => { }} // TODO: Implement move
                        width={850}
                        height={550}
                    />
                </Container>
            </Container>
        </div>
    )
}

export default App
