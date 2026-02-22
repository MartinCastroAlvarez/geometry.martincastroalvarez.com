import { Container, Button, Buttons, Text } from '@geometry/ui'
import type { Vertex } from './types'
import { Undo, Target, Trash2, Check, AlertCircle, Square } from 'lucide-react'

interface ToolbarProps {
    outerRing: Vertex[]
    holes: Vertex[][]
    currentHole: Vertex[]
    isClosed: boolean
    isAddingHole: boolean
    onUndo: () => void
    onStartHole: () => void
    onClosePolygon: () => void
    onClear: () => void
}

export function Toolbar({
    outerRing,
    isClosed,
    isAddingHole,
    onUndo,
    onStartHole,
    onClosePolygon,
    onClear
}: ToolbarProps) {
    const vertices = outerRing
    const vertexCount = vertices.length

    return (
        <Container solid padded>
            <Container center middle>
                <Container size={3}>
                    <div className="flex items-center gap-2">
                        <Square size={16} />
                        <Text sm>
                            {vertexCount} vértices
                        </Text>
                        {isClosed ? (
                            <div className="flex items-center gap-1 text-green-500">
                                <Check size={14} />
                                <Text sm>Cerrado</Text>
                            </div>
                        ) : vertexCount >= 3 ? (
                            <div className="flex items-center gap-1 text-amber-500">
                                <AlertCircle size={14} />
                                <Text sm>Abierto</Text>
                            </div>
                        ) : null}
                    </div>
                </Container>

                <Container size={9} right>
                    <Buttons right>
                        <Button
                            onClick={onUndo}
                            disabled={vertexCount === 0 && !isAddingHole}
                            sm
                        >
                            <Undo size={16} className="mr-2" />
                            Deshacer
                        </Button>

                        <Button
                            onClick={onStartHole}
                            disabled={!isClosed || isAddingHole}
                            primary={isClosed && !isAddingHole}
                            sm
                        >
                            <Target size={16} className="mr-2" />
                            Agujero
                        </Button>

                        <Button
                            onClick={onClosePolygon}
                            disabled={isClosed || vertexCount < 3}
                            primary={!isClosed && vertexCount >= 3}
                            sm
                        >
                            <Check size={16} className="mr-2" />
                            Cerrar Polígono
                        </Button>

                        <Button
                            onClick={onClear}
                            sm
                            confirm="¿Estás seguro de que querés borrar todo?"
                        >
                            <Trash2 size={16} className="mr-2" />
                            Limpiar
                        </Button>
                    </Buttons>
                </Container>
            </Container>

            {!isClosed && vertexCount > 0 && (
                <Container top>
                    <Text xs center>
                        {vertexCount < 3
                            ? `Agregá ${3 - vertexCount} vértice${3 - vertexCount > 1 ? 's' : ''} más para cerrar el polígono`
                            : 'Hacé click cerca del primer punto (verde) para cerrar el polígono'
                        }
                    </Text>
                </Container>
            )}
        </Container>
    )
}
