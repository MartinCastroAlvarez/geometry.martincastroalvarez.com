/**
 * Draggable vertex circle; same color as Edge (theme --color-editor-stroke), no border.
 *
 * Context: Konva Circle; fill from useTheme().getColor (theme.css). No stroke.
 * dragBoundFunc clamps position to dragBounds [0,0]–[width,height] when provided.
 *
 * Example:
 *   <Vertex vertex={v} index={i} onDragMove={handleVertexDrag} onClick={handleVertexClick} />
 */

import { memo, useState } from "react";
import { Circle } from "react-konva";
import { useTheme } from "@geometry/theme";
import type { EditorVertex } from "./types";

export interface VertexProps {
    vertex: EditorVertex;
    index: number;
    isFirst?: boolean;
    isActive?: boolean;
    onDragMove?: (index: number, x: number, y: number) => void;
    onDragEnd?: (index: number) => void;
    onClick?: (index: number) => void;
    draggable?: boolean;
    /** Constrain drag within bounds [0,0] to [width,height] */
    dragBounds?: { width: number; height: number };
    /** When set, constrain drag to this rect instead of [0,0]–[dragBounds.width,dragBounds.height] */
    contentBounds?: { minX: number; minY: number; maxX: number; maxY: number };
    /** Canvas scale (zoom); used to keep visual size constant (radius divided by scale). Default 1. */
    scale?: number;
}

const VertexComponent = ({
    vertex,
    index,
    isFirst = false,
    isActive = false,
    onDragMove,
    onDragEnd,
    onClick,
    draggable = true,
    dragBounds,
    contentBounds,
    scale = 1,
}: VertexProps) => {
    const { getColor } = useTheme();
    const [isHovered, setIsHovered] = useState(false);
    const baseRadius = isActive ? 8 : isFirst ? 7 : isHovered ? 6 : 5;
    const radius = baseRadius / scale;

    const dragBoundFunc =
        onDragMove && (contentBounds || dragBounds)
            ? (pos: { x: number; y: number }) => {
                  if (contentBounds) {
                      return {
                          x: Math.max(contentBounds.minX + radius, Math.min(contentBounds.maxX - radius, pos.x)),
                          y: Math.max(contentBounds.minY + radius, Math.min(contentBounds.maxY - radius, pos.y)),
                      };
                  }
                  if (dragBounds) {
                      return {
                          x: Math.max(radius, Math.min(dragBounds.width - radius, pos.x)),
                          y: Math.max(radius, Math.min(dragBounds.height - radius, pos.y)),
                      };
                  }
                  return pos;
              }
            : undefined;

    return (
        <Circle
            x={vertex.x}
            y={vertex.y}
            radius={radius}
            fill={getColor("--color-editor-stroke")}
            strokeWidth={0}
            draggable={draggable && !!onDragMove}
            cursor="pointer"
            dragBoundFunc={dragBoundFunc}
            onDragMove={
                onDragMove
                    ? (e) => {
                          const pos = e.target.position();
                          onDragMove(index, pos.x, pos.y);
                      }
                    : undefined
            }
            onDragEnd={onDragEnd ? () => onDragEnd(index) : undefined}
            onClick={onClick ? () => onClick(index) : undefined}
            onTap={onClick ? () => onClick(index) : undefined}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            shadowBlur={isHovered || isActive ? 10 : 0}
            shadowColor="rgba(0,0,0,0.4)"
            shadowOpacity={0.5}
        />
    );
};

export const Vertex = memo(VertexComponent);
