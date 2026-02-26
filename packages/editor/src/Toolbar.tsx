import { Container, Button, Text, Buttons } from "@geometry/ui";
import { Undo, Target, Check, Trash2 } from "lucide-react";

export interface ToolbarProps {
    vertexCount: number;
    isClosed: boolean;
    isAddingHole: boolean;
    onUndo: () => void;
    onStartHole: () => void;
    onClosePolygon: () => void;
    onClear: () => void;
    readonly?: boolean;
}

export function Toolbar({
    vertexCount,
    isClosed,
    isAddingHole,
    onUndo,
    onStartHole,
    onClosePolygon,
    onClear,
    readonly = false,
}: ToolbarProps) {
    return (
        <Container solid padded spaced rounded>
            <Container middle spaced size={12}>
                <Container size={4} left middle>
                    <Text sm>{vertexCount} vértices</Text>
                    {isClosed ? (
                        <Container middle spaced left>
                            <Check size={14} />
                            <Text sm>Cerrado</Text>
                        </Container>
                    ) : vertexCount >= 3 ? (
                        <Text sm>Abierto</Text>
                    ) : null}
                </Container>
                {!readonly && (
                    <Container size={8} right middle>
                        <Buttons right>
                        <Button
                            onClick={onUndo}
                            disabled={vertexCount === 0 && !isAddingHole}
                            sm
                            icon={<Undo size={14} />}
                        >
                            Deshacer
                        </Button>
                        <Button
                            onClick={onStartHole}
                            disabled={!isClosed || isAddingHole}
                            sm
                            icon={<Target size={14} />}
                        >
                            Agujero
                        </Button>
                        <Button
                            onClick={onClosePolygon}
                            disabled={isClosed || vertexCount < 3}
                            sm
                            icon={<Check size={14} />}
                        >
                            Cerrar
                        </Button>
                        <Button onClick={onClear} sm confirm="¿Borrar todo?" icon={<Trash2 size={14} />}>
                            Limpiar
                        </Button>
                        </Buttons>
                    </Container>
                )}
            </Container>
            {!readonly && !isClosed && vertexCount > 0 && (
                <Container center>
                    <Text xs center>
                        {vertexCount < 3
                            ? `Agregá ${3 - vertexCount} vértice${3 - vertexCount > 1 ? "s" : ""} más para cerrar`
                            : "Hacé click cerca del primer punto (verde) para cerrar"}
                    </Text>
                </Container>
            )}
        </Container>
    );
}
