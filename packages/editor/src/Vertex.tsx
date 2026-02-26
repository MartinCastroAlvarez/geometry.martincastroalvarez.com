import { useState } from "react";
import { Circle } from "react-konva";
import type { EditorVertex } from "./models";

export interface VertexProps {
    vertex: EditorVertex;
    isFirst?: boolean;
    isActive?: boolean;
    onDragMove?: (x: number, y: number) => void;
    onClick?: () => void;
    draggable?: boolean;
}

export function Vertex({
    vertex,
    isFirst = false,
    isActive = false,
    onDragMove,
    onClick,
    draggable = true,
}: VertexProps) {
    const [isHovered, setIsHovered] = useState(false);
    const radius = isActive || isFirst ? 8 : isHovered ? 7 : 5;

    return (
        <Circle
            x={vertex.x}
            y={vertex.y}
            radius={radius}
            fill={isActive ? "#f59e0b" : isFirst ? "#22c55e" : "#3b82f6"}
            stroke={isHovered || isActive ? "#fff" : "#1e293b"}
            strokeWidth={isActive ? 3 : 2}
            draggable={draggable && !!onDragMove}
            onDragMove={
                onDragMove
                    ? (e) => {
                          const pos = e.target.position();
                          onDragMove(pos.x, pos.y);
                      }
                    : undefined
            }
            onClick={onClick}
            onTap={onClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            shadowBlur={isHovered || isActive ? 8 : 0}
            shadowColor="#000"
            shadowOpacity={0.25}
        />
    );
}
